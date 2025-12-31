from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple

HEADER = 0xA55A
CHANNELS = 12


def crc16_ccitt(data: bytes, poly: int = 0x1021, init: int = 0xFFFF) -> int:
    crc = init
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ poly) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


@dataclass
class RcFrame:
    seq: int
    timestamp_ms: int
    ch: List[int]
    mode: int = 0

    def clamp(self) -> None:
        self.seq &= 0xFFFF
        self.timestamp_ms &= 0xFFFFFFFF
        if len(self.ch) != CHANNELS:
            raise ValueError(f"ch must be length {CHANNELS}")
        for i, v in enumerate(self.ch):
            if v < 1100:
                self.ch[i] = 1100
            elif v > 1900:
                self.ch[i] = 1900
        self.mode &= 0xFF


# Frame layout (little-endian):
# header(2) | seq(2) | ts(4) | ch0..11 (2*12) | mode(1) | crc16(2)


def encode_frame(frame: RcFrame) -> bytes:
    frame.clamp()
    from struct import pack

    payload = pack(
        "<HHI" + "H" * CHANNELS + "B",
        HEADER,
        frame.seq,
        frame.timestamp_ms,
        *frame.ch,
        frame.mode,
    )
    crc = crc16_ccitt(payload)
    return payload + pack("<H", crc)


def decode_frame(buf: bytes) -> Tuple[RcFrame, bool]:
    from struct import unpack, calcsize

    fmt = "<HHI" + "H" * CHANNELS + "B" + "H"
    size = calcsize(fmt)
    if len(buf) != size:
        raise ValueError(f"invalid size: {len(buf)} != {size}")

    header, seq, ts, *rest = unpack(fmt, buf)
    if header != HEADER:
        raise ValueError("bad header")
    ch = list(rest[:CHANNELS])
    mode = rest[CHANNELS]
    recv_crc = rest[CHANNELS + 1]

    ok = crc16_ccitt(buf[:-2]) == recv_crc
    return RcFrame(seq=seq, timestamp_ms=ts, ch=ch, mode=mode), ok
