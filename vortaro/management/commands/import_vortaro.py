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

class Command(LabelCommand):
    help = "Import a set of xml from reta-vortaro."
    args = "[datadir]"
    label = "data directory"

    correlative_matcher = re.compile(u"(ĉ|k|nen|t)i(a|e|o|u|om)")

    
    requires_model_validation = True
    can_import_settings = True
    
    def handle_label(self, data_dir, **options):
        print("Importing data from '%s'." % data_dir)
        #confirm = raw_input("Would you like to oblitarate the words table first? (yes/no): ")
        #while confirm not in ["yes", "no"]:
        #    confirm = raw_input('Please enter either "yes" or "no": ')
        #if confirm == "yes":
        #    print("The table has been obliterated!")
        #elif confirm == "no":
        #    print("Table left alone.")

        problem_words = []
        parser = etree.XMLParser(load_dtd=True)
        for datafilename in glob.glob(os.path.join(data_dir, "*.xml")):
            #print("Importing %s" % datafilename)
            data = etree.parse(datafilename, parser)
            
            mrk = data.xpath("/vortaro/art")[0].attrib["mrk"]
            
            begining = ""
            word = None
            ending = None
            ofc = None
            kap = data.xpath("/vortaro/art/kap")[0]
            if kap.text:
                begining = kap.text.strip()
            for i in kap:
                if i.tag == "ofc":
                    ofc = i.text
                    if i.tail and i.tail.strip():
                        begining += i.tail.strip()
                elif i.tag == "rad":
                    word = i.text.strip()
                    if i.tail and i.tail.strip():
                        ending = i.tail.strip()
                elif i.tag == "fnt":
                    pass # Ignoring sources for now.
                else:
                    msg = "Unknown tag %s on\n%s" % (i.tag, etree.tostring(kap))
                    raise(Exception(msg))
            

            try:
                (word, word_type) = self._interpret_word(begining, word.strip(), ending)
            except Exception, e:
            #    msg = e.message + "\non file %s" % datafilename
            #    print(msg)
                #raise Exception("Error processing file '%s': %s" % (datafilename, e.message))
                problem_words.append((begining, word, ending))
            
            print("word: %s\t\ttype: %s\t\tofc: %s" % (word, word_type, ofc))
        #else:
        #    print("No file found on '%s'." % datafilename)
        print("Done")

        for (begining, word, ending) in problem_words:
            print("problem word: begining: %s\tword: %s\tending: %s" % (begining, word, ending))
        print("%s problem words." % len(problem_words))

    def _interpret_word(self, begining, word, ending):
        #TODO: find out what this exceptions are.
        if word in [u"plus"]:
            return (word, "mathematical operation")
        elif word in [u"hodiaŭ"]:
            return (word, "time")
        elif word in [u"kaj", u"ankaŭ", u"malgraŭ", u"ambaŭ", u"ĵus", u"preskaŭ", u"ĉu", u"sed", u"aŭ", u"da", u"de", u"el", u"la", u"en"]:
            return (word, "connector")
        elif word in [u"unu", u"du", u"tri", u"kvar", u"kvin", u"ses", u"sep", u"ok", u"naŭ", u"dek", u"cent", u"mil"]:
            return (word, "number")
        elif re.match(self.correlative_matcher, word):
            return (word, "correlative")
        elif word in [u"trans", u"ĝis", u"ĉe"]:
            return (word, "preposition")
        elif word in [u"mi", u"ni", u"ili", u"li", u"ŝi", u"ĝi", u"ĉi"]:
            return (word, "personal pronoun")
        elif word in [u"ankoraŭ", u"almenaŭ", u"apenaŭ", u"baldaŭ", u"preskaŭ", u"eĉ", u"jam", u"jen", u"ĵus", u"morgaŭ", u"hodiaŭ", u"hieraŭ", u"nun", u"nur", u"plu", u"tre", u"tro", u"tuj", u"for",    u"des", u"ĉi"]:
            return (word, "adverb")
        elif word in [u"Kabe", u"Singapur", u"Novjork", u"Peterburg", u"Toki", u"TTT", u"Kiev", u"Ĥarkov"]:
            return (word, "name")
        elif word in [u"pum"]:
            return (word, "who knows")
        elif word == u"ordinaci" and ending == u"/o, ordin/o":
            ending = "/o"
        elif word == u"dis":
            ending = "-"
        elif word == u"knid" and ending == u"/uloj":
            word = "knidul"
            ending = "/oj"
        
        if begining == "-":
            if word in ["a", "e", "i", "o"]:
                return (word, "possible ending letter")
            elif len(word) >= 2 or (word == "i" and ending == "/"):
                return (word, "suffix, likely")
        else:
            if ending == "-":
                return (word, "prefix")
            elif ending == "/o":
                return (word, "noun")
            elif ending == "/oj":
                return (word, "plural noun")
            elif ending == "/a":
                return (word, "adjective")
            elif ending == "/aj":
                return (word, "plural adjective")
            elif ending == "/i":
                return (word, "verb")
            elif ending == "/e":
                return (word, "adverb")
            else:
                msg = "Unknown word type:\nbegining: %s\nword: %s\nending: %s" % (self._to_ascii(begining), self._to_ascii(word), self._to_ascii(ending))
                raise Exception(msg)

    def _to_ascii(self, s):
        try:
            s.encode("ascii")
            return s
        except:
            return repr(s)
