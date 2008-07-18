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
        msg = "Word '%s'" % self._to_ascii(self.root)
        if self.begining is not None:
            msg += ", begining with '%s'" % self._to_ascii(self.begining)
        if self.ending is not None:
            msg += ", ending with '%s'" % self._to_ascii(self.ending)
        msg += " is of unknown type."
        return msg
    
    def __unicode__(self):
        msg = "Word '%s'" % self.root
        if self.begining is not None:
            msg += ", begining with '%s'" % self.begining
        if self.ending is not None:
            msg += ", ending with '%s'" % self.ending
        msg += " is of unknown type."
        return msg
    
    def _to_ascii(self, s):
        try:
            s.encode("ascii")
            return s
        except:
            return repr(s)

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
        #elif confirm == "no":
        #    print("Table left alone.")
        
        problem_words = []
        
        def import_file(filename):
            try:
                self.import_file(filename)
            except UnknownWordType, e:
                problem_words.append(e)
        
        if os.path.isdir(data_dir):
            for filename in glob.glob(os.path.join(data_dir, "*.xml")):
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
        data = etree.parse(filename, self._parser)
        
        mrk = data.xpath("/vortaro/art")[0].attrib["mrk"]
        begining, root, ending, ofc = self._parse_kap(
            data.xpath("/vortaro/art/kap")[0])
        word_type = self._infer_word_type(begining, root.strip(), ending)
        ro = models.Root.objects.create(root=root)
        ro.natural_ending=ending
        ro.word_type=word_type
        ro.ofc=ofc
        ro.mrk=mrk
        ro.save()
        print(u"word: %s\t\ttype: %s\t\tofc: %s" % (root, word_type, ofc))
    
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
            elif i.tag == "rad":
                root = i.text.strip()
                if i.tail and i.tail.strip():
                    ending = i.tail.strip()
            elif i.tag == "fnt":
                pass # Ignoring sources for now.
            else:
                msg = "Unknown tag %s on\n%s" % (i.tag, etree.tostring(kap))
                raise(Exception(msg))
        
        if ending and ending[0] == "/":
            ending = ending [1:]
        
        return begining, root, ending, ofc

    def _infer_word_type(self, begining, root, ending):
        #TODO: find out what this exceptions are.
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
        elif root in [u"pum"]:
            return "who knows"
        #elif root == u"ordinaci" and ending == u"/o, ordin/o":
        #    ending = "/o"
        #elif root == u"dis":
        #    ending = "-"
        #elif root == u"knid" and ending == u"/uloj":
        #    root = "knidul"
        #    ending = "/oj"
        
        if begining == "-":
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
