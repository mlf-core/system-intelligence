"""Tests for gpu_info module."""

import collections.abc
import unittest

from system_intelligence.gpus_info import GpusInfo


class Tests(unittest.TestCase):

    def test_query_gpus(self):
        gpu_info = GpusInfo()
        info = gpu_info.query_gpus()
        self.assertIsInstance(info, collections.abc.Sequence)
