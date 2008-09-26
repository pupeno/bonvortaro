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

class TLD(object):
    def __init__(self, lit=None):
        self.lit = lit
    
    def __unicode__(self):
        return self.lit

class Command(LabelCommand):
    help = "Import an xml or a set of xml from reta-vortaro."
    args = "[datadir or datafile]"
    label = "data directory or file"

    correlative_matcher = re.compile(u"(ĉ|k|nen|t)i(a|e|o|u|om)")
    
    requires_model_validation = True
    can_import_settings = True
    
    def __init__(self, *args, **kwargs):
        LabelCommand.__init__(self, *args, **kwargs)
        self._parser = etree.XMLParser(load_dtd=True)
    
    def handle_label(self, data_dir, **options):
        #confirm = raw_input("Would you like to oblitarate the words table first? (yes/no): ")
        #while confirm not in ["yes", "no"]:
        #    confirm = raw_input('Please enter either "yes" or "no": ')
        #if confirm == "yes":
        #    print("The table has been obliterated!")
        models.Root.objects.all().delete()
        models.Word.objects.all().delete()
        #elif confirm == "no":
        #    print("Table left alone.")
        
        problem_words = []
        
        def import_file(filename):
            try:
                self.import_file(filename)
            except UnknownWordType, e:
                problem_words.append(e)

        
        if os.path.isdir(data_dir):
            filenames = glob.glob(os.path.join(data_dir, "*.xml"))
            filenames.sort()
            for filename in filenames:
                import_file(filename)
            else:
                print("No file found on '%s'." % filename)
        else:
            import_file(data_dir)
        print("Done.")
        
        for word in problem_words:
            print(unicode(word))
        if len(problem_words) > 1:
            print("%s problem words." % len(problem_words))
    
    def import_file(self, filename):
        print("Importing data from '%s'." % filename)
        
        for art in etree.parse(filename, self._parser).xpath("/vortaro/art"):
            # Process the root word.
            mrk = art.attrib["mrk"]
            
            assert len(art.findall("kap")) == 1, "An art has more than one kap."
            begining, root, ending, ofc = self._parse_kap(art.find("kap"))
            assert root is not None, "Found missing root word in kap in art."
            
            try:
                kind = self._infer_word_kind(begining, root.strip(), ending)
            except UnknownWordType, e:
                kind = "unknown"
            
            ro = models.Root.objects.create(root=root)
            ro.begining = begining
            ro.ending = ending
            
            ro.kind = kind

            ro.ofc = ofc
            ro.mrk = mrk

            ro.save()
            
            print(u"root: %s\tbegining: %s\tending: %s\ttype: %s\tofc: %s" %
                  (root, begining, ending, kind, ofc))
            
            for drv in art.findall("drv"):
                 mrk, begining, root, ending, kind, ofc = self._parse_drv(drv)
                 
                 word = begining + ro.root + ending
                 if root.lit:
                     word = root.lit + word[1:]
                 print(u"\t\tword: %s" % word)
                 wo = models.Word.objects.create(
                     word=word,
                     kind=kind,
                     root=ro,
                     begining=begining,
                     ending=ending,
                     ofc=ofc,
                     mrk=mrk)
    
    def _parse_kap(self, kap):
        begining = ""
        root = ""
        ending = ""
        ofc = ""
        #fnt = ""
        
        if kap.text:
            begining = kap.text.strip()
        for i in kap:
            if i.tag == "ofc":
                ofc = i.text or ""
                if i.tail and i.tail.strip():
                    begining += i.tail.strip()
            elif i.tag == "rad" or i.tag == "tld":
                if i.tag == "rad":
                    root = i.text.strip()
                else:
                    if "lit" in i.attrib:
                        root = TLD(lit=i.attrib["lit"])
                    else:
                        root = TLD()
                if i.tail and i.tail.strip():
                    ending = i.tail.strip()
            elif i.tag == "fnt":
                pass # TODO: return the fnt when it's used for something.
            elif i.tag == "var":
                pass # TODO: parse variations and return them.
            else:
                msg = "Unknown tag %s on\n%s" % (i.tag, etree.tostring(kap))
                raise(Exception(msg))
        
        if ending and ending[0] == "/":
            ending = ending [1:]
        
        # Handle exceptions
        if begining == "ilo" and root == "":
            begining = ""
            root = TLD()
            ending = "o"
        elif begining == u"nedaŭra planto" and root == "":
            begining = u"nedaŭra"
            root = TLD()
            ending = "o"
        elif begining == u"naĝoveziko,":
            begining = u"naĝo"
            root = TLD()
            ending = "o"
        
        return begining, root, ending, ofc
    
    def _parse_drv(self, drv):
        mrk = drv.attrib["mrk"]
        
        assert len(drv.findall("kap")) == 1, "A drv has more than one kap."
        begining, root, ending, ofc = self._parse_kap(drv.find("kap"))
        assert isinstance(root, TLD), "Found spurious root word, '%s', in kap in drv, with begining: '%s' and ending: '%s'." % (root, begining, ending)
        
        try:
            kind = self._infer_word_kind(begining, root, ending)
        except UnknownWordType, e:
            kind = ""
        
        print(u"\troot.lit: %s\tbegining: %s\tending: %s\ttype: %s\tofc: %s" %
              (root.lit, begining, ending, kind, ofc))

        return mrk, begining, root, ending, kind, ofc
    
    def _infer_word_kind(self, begining, root, ending):
        #TODO: find out what this exceptions are.
        if isinstance(root, str):
            if root in [u"plus"]:
                return "mathematical operation"
            elif root in [u"hodiaŭ"]:
                return "time"
            elif root in [u"kaj", u"ankaŭ", u"malgraŭ", u"ambaŭ", u"ĵus", u"preskaŭ", u"ĉu", u"sed", u"aŭ", u"da", u"de", u"el", u"la", u"en"]:
                return "connector"
            elif root in [u"unu", u"du", u"tri", u"kvar", u"kvin", u"ses", u"sep", u"ok", u"naŭ", u"dek", u"cent", u"mil"]:
                return "number"
            elif re.match(self.correlative_matcher, root):
                return "correlative"
            elif root in [u"trans", u"ĝis", u"ĉe"]:
                return "preposition"
            elif root in [u"mi", u"ni", u"ili", u"li", u"ŝi", u"ĝi", u"ĉi"]:
                return "personal pronoun"
            elif root in [u"ankoraŭ", u"almenaŭ", u"apenaŭ", u"baldaŭ", u"preskaŭ", u"eĉ", u"jam", u"jen", u"ĵus", u"morgaŭ", u"hodiaŭ", u"hieraŭ", u"nun", u"nur", u"plu", u"tre", u"tro", u"tuj", u"for",    u"des", u"ĉi"]:
                return "adverb"
            elif root in [u"Kabe", u"Singapur", u"Novjork", u"Peterburg", u"Toki", u"TTT", u"Kiev", u"Ĥarkov"]:
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
