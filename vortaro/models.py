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
        return u"%s %s %s" % (self.begining, self.root, self.ending)

class Word(models.Model):
    word = models.CharField(max_length=70)
    kind = models.CharField(max_length=70, blank=True) #, choices=WORD_TYPES)
    first = models.BooleanField()
    
    # Not used, unknown or Retavortaro specific.
    root = models.ForeignKey(Root)
    begining = models.CharField(max_length=70, blank=True)
    ending = models.CharField(max_length=70, blank=True)
    ofc = models.CharField(max_length=70, blank=True)
    #fnt = models.CharField(max_length=20)
    mrk = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return u"%s %s %s" % (self.begining, self.root.root, self.ending)
