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

import import_vortaro
import random
import unittest
import StringIO

class TestElementToString(unittest.TestCase):
    def setUp(self):
        self._command = import_vortaro.Command()
    
    def test_text_tags_subtags_and_tails(self):
        text_to_get = "blah <a>bleh</a><b>blih <c>bloh</c> bluh</b> blah"
        element = self.make_wrapped_element(text_to_get)
        
        self.assertEqual(self._command._element_to_string(element),
                         text_to_get)

    def test_no_text_no_tail(self):
        text_to_get = "<a>bleh</a><b>blih <c>bloh</c> bluh</b>"
        element = self.make_wrapped_element(text_to_get)
        
        self.assertEqual(self._command._element_to_string(element),
                         text_to_get)
        
    def make_wrapped_element(self, inner_text):
        """Return inner_text wrapped in <removeme> tags and parsed."""
        return self._command._parse_xml(
            StringIO.StringIO("<removeme>%s</removeme>" % inner_text)).getroot()
        
        
    
        

