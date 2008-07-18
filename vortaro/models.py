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
    natural_ending = models.CharField(max_length=70, blank=True)

    word_type = models.CharField(max_length=70) #, choices=WORD_TYPES)
    
    # Not used or unknown.
    ofc = models.CharField(max_length=70)
    #fnt = models.CharField(max_length=20)
    
    # Reta-vortaro specific.
    mrk = models.CharField(max_length=100)

    class Admin:
        list_display = ("root", "natural_ending", "word_type", "ofc")
        list_filter = ["natural_ending", "word_type", "ofc"]

