"""Tests for software_info module."""

import collections.abc
import unittest

from system_intelligence.software_info import SoftwareInfo


class Tests(unittest.TestCase):

    def test_query_software(self):
        sw_info = SoftwareInfo()
        info = sw_info.query_software()
        self.assertIsInstance(info, collections.abc.Mapping)
