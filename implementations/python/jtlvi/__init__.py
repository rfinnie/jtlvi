#!/usr/bin/env python3

# jtlvi - Just TLV It!
# Copyright (c) 2018 Ryan Finnie
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import struct
import sys

assert sys.version_info > (3, 4)


class Error(Exception):
    pass


def _assert(assertion, text):
    if assertion:
        return
    raise Error(text)


def bsd_checksum(input):
    """Calculate the BSD checksum of an input.

    :param input:
        Input to checksum, bytes-like object.

    :return:
        Checksum integer of the input, 0-65535 (inclusive).
    """
    checksum = 0
    for ch in input:
        checksum = (checksum >> 1) + ((checksum & 1) << 15)
        checksum += ch
        checksum &= 0xFFFF
    return checksum


def dumps(input, sort=True, trailer=True, padded_length=0, padding_bytes=b"\x00"):
    """Encode an iterable into a JTLVI message.

    Any errors encountered during encoding will be raised as a
    jtlvi.Error() exception.

    :param input:
        Input to encode.  May be a list of key/value tuples, or a
        dict-like iterable (dict, OrderedDict, etc).  Keys must be
        integers between 0 and 65534 (inclusive), and values must be
        bytes-like objects (bytes or bytearray).

    :param sort:
        If True, items are sorted by key before being encoded.

    :param trailer:
        If True, last-element sentinel 65535 is added as a final
        element.  Even if False, it may be set to True if needed (such
        as when adding padding).

    :param padded_length:
        If non-zero, the message will be padded to a minimum length.  If
        the encoded message is already greater than or equal to this
        length, no padding is added.

    :param padding_bytes:
        A bytes object of one or more bytes to be used as a repeating
        sequence when padding.

    :return:
        Returns a bytes object containing the encoded JTLVI message.
    """
    _assert(
        isinstance(input, (dict, list, tuple)),
        "Input must be a dict, or list of tuples",
    )
    if hasattr(input, "items"):
        input_items = input.items()
    else:
        input_items = input
    if sort:
        input_items = sorted(input_items)

    # Magic number 0xd40e and temporarily-zeroed checksum
    output = bytearray(b"\xd4\x0e\x00\x00")

    for (t, v) in input_items:
        # T must be a postive non-zero integer
        _assert(isinstance(t, int), "Tag {} must be an integer".format(t))
        # T=65535 is reserved for explicit EOM
        _assert(
            0 <= t <= 65534, "Tag {} must be between 0 and 65534, inclusive".format(t)
        )
        # V must be bytearray or bytes
        _assert(
            isinstance(v, (bytearray, bytes)),
            ("Value for tag {} must be bytes or bytearray " + "object, not {}").format(
                t, type(v)
            ),
        )

        # Pack T (16-bit big-endian)
        output += struct.pack("!H", t)
        # Pack L (16-bit big-endian)
        output += struct.pack("!H", len(v))
        # Append V
        output += v

    # Add optional padding, a trailer is required if so
    if (padded_length > 0) and (len(output) < padded_length):
        trailer = True
    if trailer:
        output += b"\xff\xff\x00\x00"
    if len(output) < padded_length:
        pad_target = padded_length - len(output)
        padding = padding_bytes * int(pad_target / len(padding_bytes) + 1)
        output += padding[0:pad_target]

    # Calculate and inject the checksum
    output[2:4] = struct.pack("!H", bsd_checksum(output))

    return bytes(output)


def dump(input, fp, **kwargs):
    fp.write(dumps(input, **kwargs))


def loads(input):
    """Decode a JTLVI message to a list of key/value tuples.

    Any errors encountered during decoding will be raised as a
    jtlvi.Error() exception.

    :param input:
        Input to decode.  Must be a bytes object containing a valid
        JTLVI message.

    :return:
        Returns a list of key/value tuples.  Return may be given to
        dict() or OrderedDict(), but as the JTLVI format allows for
        duplicated and out-of-order tags, dicts may lose information
        compared to the original dumped message.
    """
    input_len = len(input)
    output = []

    # Check correct magic number
    _assert(input[0:2] == b"\xd4\x0e", "Unknown magic number {}".format(input[0:2]))
    # Check input is a valid length (at least 4 bytes)
    _assert(input_len >= 4, "Incorrect input length {}".format(input_len))
    # Verify the checksum
    input_checksum = struct.unpack("!H", input[2:4])[0]
    input_zeroed = b"\xd4\x0e\x00\x00" + input[4:]
    calculated_checksum = bsd_checksum(input_zeroed)
    _assert(
        calculated_checksum == input_checksum,
        "Incorrect checksum (calculated {}, saw {})".format(
            calculated_checksum, input_checksum
        ),
    )

    # Begin looping through TLVs
    pos = 4
    while input_len > pos:
        # TLV must be at least 4 bytes (2 byte T, 2 byte L, 0+ byte V)
        _assert(
            input_len >= (pos + 4),
            "Position {}: Attempted to read T+L past EOM".format(pos),
        )
        tag = struct.unpack("!H", input[pos : pos + 2])[0]
        # T=65535 is reserved for explicit EOM; stop processing if seen
        if tag == 65535:
            break
        length = struct.unpack("!H", input[pos + 2 : pos + 4])[0]
        # Make sure L does not read past EOM
        _assert(
            input_len >= (pos + 4 + length),
            "Position {}: Attempted to read T+L+V past EOM".format(pos),
        )
        value = input[pos + 4 : pos + 4 + length]
        output.append((tag, value))
        pos += 4 + length

    return output


def load(fp, **kwargs):
    return loads(fp.read(), **kwargs)


def main(argv):
    import argparse
    import pickle

    parser = argparse.ArgumentParser(
        description="jtlvi", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "action",
        choices=["pickle-to-jtlvi", "jtlvi-to-pickle"],
        help="action to perform",
    )
    args = parser.parse_args(argv[1:])

    if args.action == "pickle-to-jtlvi":
        dump(pickle.load(sys.stdin.buffer), sys.stdout.buffer)
    elif args.action == "jtlvi-to-pickle":
        pickle.dump(load(sys.stdin.buffer), sys.stdout.buffer, protocol=3)


def module_init():
    if __name__ == "__main__":
        sys.exit(main(sys.argv))


module_init()
