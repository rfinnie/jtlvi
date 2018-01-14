# JTLVI Message Format: Just TLV It!

# Background

The authors were discussing what comprises a good binary message format, specifically for use in datagram network communication, but also in general.  This was in response to a message specification which shall remain nameless, but had features such as requiring that the parser know that tag 18 was followed by an 8-byte value.  That is to say, the parser must implement the entire specification to be able to parse even an arbitrary message.

We came to the follow conclusions:

* A message format should be able to be programatically identified as such, via a magic number.
* A message format should include an explicit version number, or (preferably) be compatible in both directions. [Tag-Length-Value (TLV)](https://en.wikipedia.org/wiki/Type-length-value) allows parsers to parse a complete message, even when the parser doesn't know the structure of a particular tag.
* The endianness of the message format should be explicitly documented.
* Messages should contain a unique ID which allows for identification/response, duplicate filtering, etc.
* Messages should guard against short reads, by including a built-in checksum, explicitly stating the number of elements in the message, including an explicit last-element sentinel, etc.
* Messages should be able to be padded to arbitrary lengths at creation time, without affecting the content of the message's elements.

These are good guidelines in general, but often you just want a simple message format for a specialized purpose (say, UDP communication between two devices), without needing to explicitly think about whether your new format satisfies these.  Enter **JTLVI: Just TLV It!**

# Message format

A JTLVI message is network byte order (big endian), and includes the following elements:

* 2-byte magic number 0xd40e.  (These bytes were picked at random for the JTLVI format and carry no previous significance.)
* 2-byte checksum.  It is set to 0x0000 during message assembly, then replaced with the [BSD checksum](https://en.wikipedia.org/wiki/BSD_checksum) of the zeroed message once assembly is complete.
* Zero or more TLV elements, comprised of the following:
    * 2-byte integer tag between 0 and 65535 (inclusive).  Tag 65535 is reserved as an explicit last-element sentinel.  All other tag meaning is defined by the implementation.
    * 2-byte length of the value, between 0 and 65535 (inclusive).  Zero-byte value fields are explicitly permitted by setting the length to zero.
    * Variable length value, as defined in the length field above.  The structure of the tag's value is outside the scope of JTLVI's message format, and is defined by the implementation.  Tag 5 could be a big-endian integer, tag 8192 could be an arbitrary-length UTF-8 string, etc.
* Zero or more arbitrary padding bytes.  If padding is set, it must be preceded by last-element sentinel 0xffff (65535).  If no padding is set, the last-element sentinel is recommended but not required (EOM is a sufficient indicator).  Padding can be any byte value(s).  Padding is included when calculating the message's checksum.

That's it!  JTLVI messages are easy to assemble, parse and verify.  They satisfy all but one of the previously defined conditions of a good message format: Explicit message IDs are not part of JTLVI.  It's recommended an implementation make tag 0 be the message ID, but not required.

It is recommended that TLV elements be arranged by tag number (ascending), but not required.  The only hard rule is processing must stop when last-element sentinel 0xffff (65535) is reached.  A tag number may be used multiple times within a message, but whether they should depends on your application.

The checksum is meant as a simple check against transmission or storage errors, and is not meant to be comprehensive.  The BSD checksum algorithm was chosen because it is easy to implement.

## Examples

The following examples are hex dumps of valid JTLVI messages.  They are split by whitespace along logical partitions to make it easier to visually parse.

```
d40e 001e
```

* 4-byte message
* Magic number 0xd40e
* Message checksum 0x001e
* Zero TLV elements, zero padding, but still a valid message

```
d40e 28d1 007b 0002 01c8
```

* 10-byte message
* Magic number 0xd40e
* Message checksum 0x28d1
* Tag 123, length 2, value 0x01c8 (i.e. integer 456)
* No explicit last-element sentinel
* Zero padding

```
d40e c5aa 0002 0004 5a40931d 04d2 0000 162e 000b 48656c6c6f2c20e2988321 ffff 0000 f0f0f0f0f0
```

* 40-byte message
* Magic number 0xd40e
* Message checksum 0xd31f
* Tag 2, length 4, value 0x5a40931d (i.e. integer 1514181405)
* Tag 1234, length 0, no value (but still a valid message element)
* Tag 5678, length 11, value 0x48656c6c6f2c20e2988321 (i.e. UTF-8 string "Hello, ☃!")
* Tag 65535, length 0, no value (last-element sentinel)
* 5 bytes of padding, 0xf0f0f0f0f0

## License

Copyright © 2018 Ryan Finnie.  This specification is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/).  Implementations of the specification may be under different licenses.