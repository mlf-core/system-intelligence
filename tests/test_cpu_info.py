"""Tests for cpu_info module."""

import unittest

from system_intelligence.cpu_info import CpuInfo


class Tests(unittest.TestCase):

    def test_cpu_cache_size(self):
        cpu_info = CpuInfo()
        if cpu_info.OS != 'darwin':
            info = cpu_info._get_cache_size(1, {'l1_cache_size': 512})
            self.assertIsInstance(info, str)
            self.assertEqual(info, '512 B')

    def test_cpu_cache_size_with_units(self):
        cpu_info = CpuInfo()
        if cpu_info.OS != 'darwin':
            info = cpu_info._get_cache_size(1, {'l1_cache_size': '512'})
            self.assertIsInstance(info, str)
            self.assertEqual(info, '512 B')
            info = cpu_info._get_cache_size(1, {'l1_cache_size': '512000'})
            self.assertIsInstance(info, str)
            self.assertEqual(info, '500 KiB')
            info = cpu_info._get_cache_size(1, {'l1_cache_size': '512000000'})
            self.assertIsInstance(info, str)
            self.assertEqual(info, '488.28 MiB')
            info = cpu_info._get_cache_size(1, {'l1_cache_size': '2000000000'})
            self.assertIsInstance(info, str)
            self.assertEqual(info, '1.86 GiB')
            info = cpu_info._get_cache_size(1, {'l1_cache_size': '4000000000000'})
            self.assertIsInstance(info, str)
            self.assertEqual(info, '3.64 TiB')
