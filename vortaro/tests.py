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

import unittest
import models

class ToXSistemoTest(unittest.TestCase):
    def test_to_xsistemo(self):
        self.assertEquals(
            'CxcxGxgxHxhxJxjxSxsxUxux',
            models._to_xsistemo(u"ĈĉĜĝĤĥĴĵŜŝŬŭ"))