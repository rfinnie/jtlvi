#!/usr/bin/env python3

import unittest
import jtlvi


class TestBSDChecksum(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(jtlvi.bsd_checksum(b''), 0)

    def test_zero(self):
        self.assertEqual(jtlvi.bsd_checksum(b'\x00'), 0)

    def test_ff(self):
        self.assertEqual(jtlvi.bsd_checksum(b'\xff'*128), 62459)

    def test_foo(self):
        self.assertEqual(jtlvi.bsd_checksum(b'foo'), 192)


if __name__ == '__main__':
    unittest.main()

