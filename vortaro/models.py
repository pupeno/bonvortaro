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

from django.db import models

#WORD_TYPES = (
#    ("s", "suffix"),
#    ("p", "prefix"),
#    ("n", "noun"),
#    ("nn", "plural noun"),
#    ("a", "adjective"),
#    ("aa", "plural adjective"),
#    ("v", "verb"),
#    ("d", "adverb")
#)

def _to_xsistemo(s):
    """Turn a nice unicode string into an hideous x-sistemo one."""
    replacements = [
        (u"Ĉ", "Cx"),
        (u"ĉ", "cx"),
        (u"Ĝ", "Gx"),
        (u"ĝ", "gx"),
        (u"Ĥ", "Hx"),
        (u"ĥ", "hx"),
        (u"Ĵ", "Jx"),
        (u"ĵ", "jx"),
        (u"Ŝ", "Sx"),
        (u"ŝ", "sx"),
        (u"Ŭ", "Ux"),
        (u"ŭ", "ux"),
    ]
    
    for old, new in replacements:
        s = s.replace(old, new)
    
    try:
        s = s.encode("ascii")
        return s
    except:
        return repr(s)

class Root(models.Model):
    root = models.CharField(max_length=70)
    kind = models.CharField(max_length=70, blank=True) #, choices=WORD_TYPES)
    
    # Not used, unknown or Retavortaro specific.
    begining = models.CharField(max_length=70, blank=True)
    ending = models.CharField(max_length=70, blank=True)
    ofc = models.CharField(max_length=70, blank=True)
    #fnt = models.CharField(max_length=20)
    mrk = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return self.root

class Word(models.Model):
    language = models.CharField(max_length=3)
    root = models.ForeignKey(Root, blank=True, null=True)
    word = models.CharField(max_length=70)
    kind = models.CharField(max_length=70, blank=True) #, choices=WORD_TYPES)
    
    # Not used, unknown or Retavortaro specific.
    begining = models.CharField(max_length=70, blank=True)
    ending = models.CharField(max_length=70, blank=True)
    ofc = models.CharField(max_length=70, blank=True)
    #fnt = models.CharField(max_length=20)
    mrk = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return self.word

    def revo_url(self):
        """Returns the URL for this word in Reta Vortaro."""
        return "http://reta-vortaro.de/revo/art/%s.html#%s" % (_to_xsistemo(self.root.root), self.mrk)

class Definition(models.Model):
    word = models.ForeignKey(Word)
    definition = models.TextField()

    def __unicode__(self):
        return self.definition
