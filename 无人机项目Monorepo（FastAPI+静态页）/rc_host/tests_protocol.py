import unittest
from protocol import RcFrame, encode_frame, decode_frame, crc16_ccitt


class TestRcProtocol(unittest.TestCase):
    def test_roundtrip(self):
        f = RcFrame(seq=1, timestamp_ms=123456, ch=[1500] * 12, mode=2)
        b = encode_frame(f)
        f2, ok = decode_frame(b)
        self.assertTrue(ok)
        self.assertEqual(f2.seq, 1)
        self.assertEqual(f2.timestamp_ms, 123456)
        self.assertEqual(f2.ch, [1500] * 12)
        self.assertEqual(f2.mode, 2)

    def test_crc_corrupt(self):
        f = RcFrame(seq=2, timestamp_ms=1, ch=[1600] * 12, mode=1)
        b = bytearray(encode_frame(f))
        b[-1] ^= 0xFF  # corrupt crc
        _, ok = decode_frame(bytes(b))
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
