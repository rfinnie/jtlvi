import io
import unittest
import unittest.mock

import jtlvi


def _test_module_init(module, main_name="main"):
    with unittest.mock.patch.object(
        module, main_name, return_value=0
    ), unittest.mock.patch.object(
        module, "__name__", "__main__"
    ), unittest.mock.patch.object(
        module.sys, "exit"
    ) as exit:
        module.module_init()
        return exit.call_args[0][0] == 0


class TestCLI(unittest.TestCase):
    pickle_bytes = (
        b"\x80\x03]q\x00(K\x01C\x03fooq\x01\x86q\x02K\x02C\x03barq\x03\x86q\x04e."
    )
    jtlvi_bytes = (
        b"\xd4\x0e\xef\x7f\x00\x01\x00\x03foo\x00\x02\x00\x03bar\xff\xff\x00\x00"
    )

    def test_module_init(self):
        self.assertTrue(_test_module_init(jtlvi))

    def test_pickle_to_jtlvi(self):
        stdin = unittest.mock.MagicMock()
        stdin.buffer = io.BytesIO(self.pickle_bytes)
        stdout = unittest.mock.MagicMock()
        stdout.buffer = io.BytesIO()
        with unittest.mock.patch.object(
            jtlvi.sys, "stdin", stdin
        ), unittest.mock.patch.object(jtlvi.sys, "stdout", stdout):
            jtlvi.main(["jtlvi", "pickle-to-jtlvi"])
            stdout.buffer.seek(0)
            self.assertEqual(stdout.buffer.read(), self.jtlvi_bytes)

    def test_jtlvi_to_pickle(self):
        stdin = unittest.mock.MagicMock()
        stdin.buffer = io.BytesIO(self.jtlvi_bytes)
        stdout = unittest.mock.MagicMock()
        stdout.buffer = io.BytesIO()
        with unittest.mock.patch.object(
            jtlvi.sys, "stdin", stdin
        ), unittest.mock.patch.object(jtlvi.sys, "stdout", stdout):
            jtlvi.main(["jtlvi", "jtlvi-to-pickle"])
            stdout.buffer.seek(0)
            self.assertEqual(stdout.buffer.read(), self.pickle_bytes)
