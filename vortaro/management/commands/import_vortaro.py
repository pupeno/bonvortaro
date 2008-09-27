# -*- coding: utf-8 -*-
# Copyright (C) 2008  José Pablo Fernández Silva
#
# This file is part of Bonvrtaro.
#
# Bonvortaro is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Bonvortaro is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along
# with Bonvortaro.  If not, see <http://www.gnu.org/licenses/>.

from django.core.management.base import LabelCommand
import glob
import os
from lxml import etree
import pdb
import re

from vortaro import models

class UnknownWordType(Exception):
    def __init__(self, begining, root, ending):
        self.begining = begining
        self.root = root
        self.ending = ending
    
    def __str__(self):
        return models._to_xsistemo(unicode(self))
    
    def __unicode__(self):
        msg = "Word '%s'" % self.root
        if self.begining is not None:
            msg += ", begining with '%s'" % self.begining
        if self.ending is not None:
            msg += ", ending with '%s'" % self.ending
        msg += " is of unknown type."
        return msg

class UnexpectedTag(Exception):
    def __init__(self, tag):
        self.tag = tag
    
    def __str__(self):
        return "\n%s in\n%s" % (
            etree.tostring(self.tag), etree.tostring(self.tag.getparent()))

class TLD(object):
    def __init__(self, lit=None):
        self.lit = lit
    
    def __unicode__(self):
        if self.lit is not None:
            return self.lit
        else:
            return u""

class Command(LabelCommand):
    help = "Import an xml or a set of xml from reta-vortaro."
    args = "[datadir or datafile]"
    label = "data directory or file"
    
    _correlative_matcher = re.compile(u"(ĉ|k|nen|t)i(a|e|o|u|om)")
    _models = [models.Root, models.Word, models.Definition, models.Translation]
    
    requires_model_validation = True
    can_import_settings = True
    
    def __init__(self, *args, **kwargs):
        LabelCommand.__init__(self, *args, **kwargs)
        self._verbosity = 1     # TODO: let an argument set this. Default to 1.
        self._delete = True     # TODO: let an argument set this. Default to None.
        self._exceptions = True # TODO: let an argument set this. Default to True.
        self._parser = etree.XMLParser(
            load_dtd=True, remove_blank_text=True, remove_comments=True)
    
    def handle_label(self, data_dir, **options):
        if self._delete is None:
            confirm = raw_input(
                "Would you like to oblitarate the words table first?"
                " (yes/no): ")
            while confirm not in ["yes", "no"]:
                confirm = raw_input("Please enter either \"yes\" or \"no\": ")
            if confirm == "yes":
                this._delete = True
            else:
                this._delete = False
        for model in self._models:
            self._log(1, "Deleting data on table for %s." % model)
            model.objects.all().delete()
        
        problem_words = []
        
        def import_file(filename):
            """Import a file and keep track of the problematic words."""
            try:
                self.import_file(filename)
            except Exception, e:
                problem_words.append(e)
        
        # If it is a directory, import all the XML filse inside it, otherwise,
        # just import the file.
        if os.path.isdir(data_dir):
            filenames = glob.glob(os.path.join(data_dir, "*.xml"))
            filenames.sort()
            for filename in filenames:
                import_file(filename)
            else:
                print("No file found on '%s'." % filename)
        else:
            import_file(data_dir)
        
        # Done.
        self._log(0, "Done.")
        # Report the problematic words, if any.
        for word in problem_words:
            self._log(0, unicode(word))
        if len(problem_words) > 1:
            self._log(0, "%s problem words." % len(problem_words))
    
    def import_file(self, filename):
        """Import an individual filename, turning the XML into records."""
        
        self._log(1, "Importing data from '%s'." % filename)
        
        xmltree = etree.parse(filename, self._parser)
        roots = self._parse_vortaro(xmltree.getroot())
        
        for root in roots:
            ro = models.Root.objects.create(
                root=root["root"],
                kind=root["kind"],
                begining=root["begining"],
                ending = root["ending"],
                ofc = root["ofc"],
                mrk = root["mrk"])
            self._log(1, "\tRoot: %s." % ro)

            for word in root["words"]:
                wo = models.Word.objects.create(
                    root=ro,
                    word=word["word"],
                    kind=word["kind"],
                    begining=word["begining"],
                    ending=word["ending"],
                    ofc=word["ofc"],
                    mrk=word["mrk"])
                self._log(1, u"\t\tWord: %s." % wo)
    
    def _parse_vortaro(self, vortaro):
        """Parse the root element, vortaro, generating a list of roots.

        I think it's not likely or even possible to have more than one root in a
        vortaro, but just in case, the code allows for it.
        """
        roots = []
        for vortaro_child in vortaro.getchildren():
            if vortaro_child.tag == "art":
                # An art is essentially a root word,
                root = {}
                root["mrk"] = vortaro_child.attrib["mrk"]
                # which must have only one kap.
                assert len(vortaro_child.findall("kap")) == 1, "An art, %s, has more than one kap, when it shouldn't." % root["mrk"]
                
                root["words"] = []
                for art_child in vortaro_child.getchildren():
                    if art_child.tag == "kap":
                        # kap defines what the root word looks like.
                        root["begining"], root["root"], root["ending"], root["ofc"] = self._parse_kap(vortaro_child.find("kap"))
                        assert root["root"] is not None, "A kap, in art %s, is missing the root word." % root["mrk"]
                        try:
                            root["kind"] = self._infer_word_kind(root["begining"], root["root"].strip(), root["ending"])
                        except UnknownWordType, e:
                            root["kind"] = "unknown"
                    
                    elif art_child.tag in ["adm", "bld", "dif", "ekz", "fnt",
                                           "gra", "mlg", "ref", "refgrp", "rim",
                                           "snc", "subart", "tez", "tezrad",
                                           "trd", "trdgrp", "url", "uzo"]:
                        continue # TODO: parse these tags.
                    
                    elif art_child.tag == "drv":
                        word = {}
                        word["mrk"], word["begining"], word["root"], word["ending"], word["kind"], word["ofc"] = self._parse_drv(art_child)
                        word["word"] = (word["begining"] + root["root"] +
                                        word["ending"])
                        if word["root"].lit:
                            word["word"] = word["root"].lit + word["word"][1:]
                        root["words"].append(word)
                    
                    else:
                        raise UnexpectedTag(art_child)
                
                roots.append(root)
            
            else:
                raise UnexpectedTag(vortaro_child)
        
        return roots
    
    def _parse_drv(self, drv):
        """Parse a drv tag.
        
        The result of a drv tag is a word with a bunch of properties."""
        
        word = {}
        word["mrk"] = drv.attrib["mrk"]
        
        assert len(drv.findall("kap")) == 1, "A drv has more than one kap."
        word["begining"], word["root"], word["ending"], word["ofc"] = self._parse_kap(drv.find("kap"))
        assert isinstance(word["root"], TLD), "Found spurious root word, '%s', in kap in drv, with begining: '%s' and ending: '%s'." % (word["root"], word["begining"], word["ending"])
        
        try:
            word["kind"] = self._infer_word_kind(word["begining"], word["root"], word["ending"])
        except UnknownWordType, e:
            word["kind"] = "unknown"
        
        self._log(2, u"\troot: %s\tbegining: %s\tending: %s\ttype: %s\tofc: %s" % (word["root"], word["begining"], word["ending"], word["kind"], word["ofc"]))
        
        word["definitions"] = []
        for senco in drv.findall("snc"):
            assert len(senco.findall("dif")) <= 1, "A snc, %s, has more than one dif." % senco.attrib["mrk"]
            dif = senco.find("dif")
            if dif is not None:
                definition = self._parse_dif(senco.find("dif"))
                self._log(2, u"\t\tdefinition: %s" % definition)
        
        return word["mrk"], word["begining"], word["root"], word["ending"], word["kind"], word["ofc"]
    
    def _parse_dif(self, dif):
        definition = ""
        if dif.text is not None:
            definition += dif.text
        for i in dif:
            if i.tag == "ref":
                if i.text is not None:
                    definition += i.text
                if i.tail is not None:
                    definition += i.tail
#                assert i.getchildren() == [], "A ref has a subtag."
#            else:
#                raise UnexpectedTag(i)
        return definition.strip().replace("\n", " ")
    
    def _parse_kap(self, kap):
        word = {
            "begining": "",
            "root": "",
            "ending": "",
            "ofc": "",
            #fnt: "",
        }
        
        if kap.text:
            word["begining"] = kap.text.strip()
        for i in kap:
            if i.tag == "ofc":
                word["ofc"] = i.text or ""
                if i.tail and i.tail.strip():
                    word["begining"] += i.tail.strip()
            elif i.tag == "rad" or i.tag == "tld":
                if i.tag == "rad":
                    word["root"] = i.text.strip()
                else:
                    if "lit" in i.attrib:
                        word["root"] = TLD(lit=i.attrib["lit"])
                    else:
                        word["root"] = TLD()
                if i.tail and i.tail.strip():
                    word["ending"] = i.tail.strip()
            elif i.tag == "fnt":
                pass # TODO: return the fnt when it's used for something.
            elif i.tag == "var":
                pass # TODO: parse variations and return them.
            else:
                raise UnexpectedTag(i)
        
        if word["ending"] and word["ending"][0] == "/":
            word["ending"] = word["ending"][1:]
        
        # Handle exceptions
        if self._exceptions:
            if word["begining"] == "ilo" and word["root"] == "":
                word["begining"] = ""
                word["root"] = TLD()
                word["ending"] = "o"
            elif word["begining"] == u"nedaŭra planto" and word["root"] == "":
                word["begining"] = u"nedaŭra"
                word["root"] = TLD()
                word["ending"] = "o"
            elif word["begining"] == u"naĝoveziko,":
                word["begining"] = u"naĝo"
                word["root"] = TLD()
                word["ending"] = "o"
        
        return word["begining"], word["root"], word["ending"], word["ofc"]
    
    def _infer_word_kind(self, begining, root, ending):
        #TODO: find out what this exceptions are.
        if isinstance(root, str):
            if root in [u"plus"]:
                return "mathematical operation"
            elif root in [u"hodiaŭ"]:
                return "time"
            elif root in [u"kaj", u"ankaŭ", u"malgraŭ", u"ambaŭ", u"ĵus",
                          u"preskaŭ", u"ĉu", u"sed", u"aŭ", u"da", u"de", u"el",
                          u"la", u"en"]:
                return "connector"
            elif root in [u"unu", u"du", u"tri", u"kvar", u"kvin", u"ses",
                          u"sep", u"ok", u"naŭ", u"dek", u"cent", u"mil"]:
                return "number"
            elif re.match(self._correlative_matcher, root):
                return "correlative"
            elif root in [u"trans", u"ĝis", u"ĉe"]:
                return "preposition"
            elif root in [u"mi", u"ni", u"ili", u"li", u"ŝi", u"ĝi", u"ĉi"]:
                return "personal pronoun"
            elif root in [u"ankoraŭ", u"almenaŭ", u"apenaŭ", u"baldaŭ",
                          u"preskaŭ", u"eĉ", u"jam", u"jen", u"ĵus", u"morgaŭ",  # preskaŭ is repeated in a previous conditional.
                          u"hodiaŭ", u"hieraŭ", u"nun", u"nur", u"plu", u"tre",
                          u"tro", u"tuj", u"for", u"des", u"ĉi"]:
                return "adverb"
            elif root in [u"Kabe", u"Singapur", u"Novjork", u"Peterburg",
                          u"Toki", u"TTT", u"Kiev", u"Ĥarkov"]:
                return "name"
            #elif root in [u"pum"]:
            #    return "who knows"
            #elif root == u"ordinaci" and ending == u"/o, ordin/o":
            #    ending = "/o"
            #elif root == u"dis":
            #    ending = "-"
            #elif root == u"knid" and ending == u"/uloj":
            #    root = "knidul"
            #    ending = "/oj"
        
        if begining == "-" and  isinstance(root, str):
            if root in ["a", "e", "i", "o"]:
                return "possible ending letter"
            elif len(root) >= 2 or (root == "i" and ending == "/"):
                return "suffix, likely"
        else:
            if ending == "-":
                return "prefix"
            elif ending == "o":
                return "noun"
            elif ending == "oj":
                return "plural noun"
            elif ending == "a":
                return "adjective"
            elif ending == "aj":
                return "plural adjective"
            elif ending == "i":
                return "verb"
            elif ending == "e":
                return "adverb"
            else:
                raise UnknownWordType(begining, root, ending)
    
    def _log(self, level, message):
        """Print the message if the verbosity allows for it."""
        if self._verbosity >= level:
            print(message)
            return True
        else:
            return False
