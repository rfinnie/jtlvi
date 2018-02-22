#!/usr/bin/env python3

import unittest
import jtlvi
import io


class TestDumps(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(
            jtlvi.dumps([]),
            b'\xd4\x0e\x80a\xff\xff\x00\x00'
        )

    def test_list(self):
        self.assertEqual(
            jtlvi.dumps([(1, b'foo'), (2, b'bar')]),
            b'\xd4\x0e\xef\x7f\x00\x01\x00\x03foo\x00\x02\x00\x03bar\xff\xff\x00\x00'
        )

    def test_dict(self):
        self.assertEqual(
            jtlvi.dumps({1: b'foo', 2: b'bar'}),
            b'\xd4\x0e\xef\x7f\x00\x01\x00\x03foo\x00\x02\x00\x03bar\xff\xff\x00\x00'
        )

    def test_value_bytearray(self):
        self.assertEqual(
            jtlvi.dumps([(1, bytearray([6, 212]))]),
            b'\xd4\x0e \xed\x00\x01\x00\x02\x06\xd4\xff\xff\x00\x00'
        )

    def test_sorted(self):
        self.assertEqual(
            jtlvi.dumps([(2, b'bar'), (1, b'foo')], sort=True),
            b'\xd4\x0e\xef\x7f\x00\x01\x00\x03foo\x00\x02\x00\x03bar\xff\xff\x00\x00'
        )

    def test_unsorted(self):
        self.assertEqual(
            jtlvi.dumps([(2, b'bar'), (1, b'foo')], sort=False),
            b'\xd4\x0e>a\x00\x02\x00\x03bar\x00\x01\x00\x03foo\xff\xff\x00\x00'
        )

    def test_no_trailer(self):
        self.assertEqual(
            jtlvi.dumps([], trailer=False),
            b'\xd4\x0e\x00\x1e'
        )

    def test_padding(self):
        self.assertEqual(
            jtlvi.dumps([], padded_length=32, padding_bytes=b'\xf0\x0f'),
            b'\xd4\x0e\xad\xb3\xff\xff\x00\x00\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f'
        )

    def test_padding_unused(self):
        self.assertEqual(
            jtlvi.dumps([(1, b'foo'), (2, b'bar')], padded_length=8),
            b'\xd4\x0e\xef\x7f\x00\x01\x00\x03foo\x00\x02\x00\x03bar\xff\xff\x00\x00'
        )

    def test_dump(self):
        f = io.BytesIO()
        jtlvi.dump([], f)
        f.seek(0)
        self.assertEqual(
            f.read(),
            b'\xd4\x0e\x80a\xff\xff\x00\x00'
        )


class TestDumpsExceptions(unittest.TestCase):
    def test_input_int(self):
        self.assertRaisesRegex(
            jtlvi.Error,
            "Input must be a dict, or list of tuples",
            jtlvi.dumps,
            1
        )

    def test_tag_bytes(self):
        self.assertRaisesRegex(
            jtlvi.Error,
            "Tag b'1' must be an integer",
            jtlvi.dumps,
            [(b'1', b'')]
        )

    def test_tag_float(self):
        self.assertRaisesRegex(
            jtlvi.Error,
            "Tag 1.0 must be an integer",
            jtlvi.dumps,
            [(1.0, b'')]
        )

    def test_tag_negative(self):
        self.assertRaisesRegex(
            jtlvi.Error,
            "Tag -1 must be between 0 and 65534, inclusive",
            jtlvi.dumps,
            [(-1, b'')]
        )

    def test_tag_65535(self):
        self.assertRaisesRegex(
            jtlvi.Error,
            "Tag 65535 must be between 0 and 65534, inclusive",
            jtlvi.dumps,
            [(65535, b'')]
        )

    def test_tag_high(self):
        self.assertRaisesRegex(
            jtlvi.Error,
            "Tag 99999 must be between 0 and 65534, inclusive",
            jtlvi.dumps,
            [(99999, b'')]
        )

    def test_value_str(self):
        self.assertRaisesRegex(
            jtlvi.Error,
            "Value for tag 1 must be bytes or bytearray object, not <class 'str'>",
            jtlvi.dumps,
            [(1, '')]
        )


class TestLoads(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(
            jtlvi.loads(b'\xd4\x0e\x80a\xff\xff\x00\x00'),
            []
        )

    def test_sorted(self):
        self.assertEqual(
            jtlvi.loads(b'\xd4\x0e\xef\x7f\x00\x01\x00\x03foo\x00\x02\x00\x03bar\xff\xff\x00\x00'),
            [(1, b'foo'), (2, b'bar')]
        )

    def test_unsorted(self):
        self.assertEqual(
            jtlvi.loads(b'\xd4\x0e>a\x00\x02\x00\x03bar\x00\x01\x00\x03foo\xff\xff\x00\x00'),
            [(2, b'bar'), (1, b'foo')]
        )

    def test_no_trailer(self):
        self.assertEqual(
            jtlvi.loads(b'\xd4\x0e\x00\x1e'),
            []
        )

    def test_padding(self):
        self.assertEqual(
            jtlvi.loads(b'\xd4\x0e\xad\xb3\xff\xff\x00\x00\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f'),
            []
        )

    def test_load(self):
        f = io.BytesIO(b'\xd4\x0e\x80a\xff\xff\x00\x00')
        f.seek(0)
        self.assertEqual(
            jtlvi.load(f),
            []
        )


class TestLoadsExceptions(unittest.TestCase):
    def test_magic_numer(self):
        self.assertRaisesRegex(
            jtlvi.Error,
            "Unknown magic number b'\\\\xff\\\\xff'",
            jtlvi.loads,
            b'\xff\xff\x80a\xff\xff\x00\x00'
        )

    def test_short_message(self):
        self.assertRaisesRegex(
            jtlvi.Error,
            "Incorrect input length 2",
            jtlvi.loads,
            b'\xd4\x0e'
        )

    def test_invalid_checksum(self):
        self.assertRaisesRegex(
            jtlvi.Error,
            "Incorrect checksum \\(calculated 32865, saw 65535\\)",
            jtlvi.loads,
            b'\xd4\x0e\xff\xff\xff\xff\x00\x00'
        )

    def test_short_tag(self):
        self.assertRaisesRegex(
            jtlvi.Error,
            "Position 4: Attempted to read T\\+L past EOM",
            jtlvi.loads,
            b'\xd4\x0e\x80\x08\x00\x01'
        )

    def test_past_eom(self):
        self.assertRaisesRegex(
            jtlvi.Error,
            "Position 4: Attempted to read T\\+L\\+V past EOM",
            jtlvi.loads,
            b'\xd4\x0e(`\x00\x01\xff\xff\x00\x00'
        )


if __name__ == '__main__':
    unittest.main()
