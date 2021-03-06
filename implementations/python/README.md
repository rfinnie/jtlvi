# JTLVI Message Format: Just TLV It!

https://github.com/rfinnie/jtlvi

## About

This is the Python 3 reference implementation of JTLVI, a simple binary message format.

## Example

```
>>> from struct import pack
>>> jtlvi.dumps([(1, pack('!I', 123)), (2, b'Hello!')])  # Native format is list of tuples
b'\xd4\x0e\xc4\xf5\x00\x01\x00\x04\x00\x00\x00{\x00\x02\x00\x06Hello!\xff\xff\x00\x00'
>>> jtlvi.dumps({999: pack('!f', 1.2)})  # Dicts can also be supplied
b'\xd4\x0e*q\x03\xe7\x00\x04?\x99\x99\x9a\xff\xff\x00\x00'
>>> jtlvi.loads(b'\xd4\x0e*q\x03\xe7\x00\x04?\x99\x99\x9a\xff\xff\x00\x00')
[(999, b'?\x99\x99\x9a')]
```

## License

Copyright (c) 2018 Ryan Finnie

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
