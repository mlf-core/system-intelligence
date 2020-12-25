"""Tests for cpu_info module."""

import unittest

from system_intelligence.cpu_info import CpuInfo


class Tests(unittest.TestCase):

    def test_cpu_cache_size(self):
        cpu_info = CpuInfo()
        info = cpu_info._get_cache_size(1, {'l1_cache_size': '512'})
        self.assertIsInstance(info, int)
        self.assertEqual(info, 512 * 1024)

    def test_cpu_cache_size_with_units(self):
        cpu_info = CpuInfo()
        info = cpu_info._get_cache_size(1, {'l1_cache_size': '512 kB'})
        self.assertIsInstance(info, int)
        self.assertEqual(info, 512 * 1000)
        info = cpu_info._get_cache_size(1, {'l1_cache_size': '512 KB'})
        self.assertIsInstance(info, int)
        self.assertEqual(info, 512 * 1024)
        info = cpu_info._get_cache_size(1, {'l1_cache_size': '512 KiB'})
        self.assertIsInstance(info, int)
        self.assertEqual(info, 512 * 1024)
        info = cpu_info._get_cache_size(1, {'l1_cache_size': '2 MB'})
        self.assertIsInstance(info, int)
        self.assertEqual(info, 2 * 1024 ** 2)
        info = cpu_info._get_cache_size(1, {'l1_cache_size': '4 MiB'})
        self.assertIsInstance(info, int)
        self.assertEqual(info, 4 * 1024 ** 2)
