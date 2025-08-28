from __future__ import annotations
from typing import Optional, Union, Literal
from os import urandom
import hmac, hashlib

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ByteLike = Union[bytes, bytearray, int]

# פרמטרים קבועים
NONCE_LEN = 16  # 128-bit CTR nonce/IV
TAG_LEN = 32    # HMAC-SHA256 tag length (bytes)

def pack_packet(nonce: bytes, ct: bytes, tag: bytes) -> bytes:
    """אורז חבילה בפורמט: | 16B nonce | N bytes ciphertext | 32B tag |"""
    if not (isinstance(nonce, (bytes, bytearray)) and len(nonce) == NONCE_LEN):
        raise ValueError("nonce must be 16 bytes")
    if not (isinstance(tag, (bytes, bytearray)) and len(tag) == TAG_LEN):
        raise ValueError("tag must be 32 bytes (HMAC-SHA256)")
    if not isinstance(ct, (bytes, bytearray)):
        raise TypeError("ciphertext must be bytes")
    return bytes(nonce) + bytes(ct) + bytes(tag)


def unpack_packet(packet: bytes) -> tuple[bytes, bytes, bytes]:
    """מפענח חבילה בפורמט לעיל ומחזיר (nonce, ciphertext, tag)."""
    if not isinstance(packet, (bytes, bytearray)):
        raise TypeError("packet must be bytes")
    if len(packet) < NONCE_LEN + TAG_LEN:
        raise ValueError("packet too short")
    nonce = bytes(packet[:NONCE_LEN])
    tag = bytes(packet[-TAG_LEN:])
    ct = bytes(packet[NONCE_LEN:-TAG_LEN])
    return nonce, ct, tag


# =========================
# כלי עזר
# =========================

def _as_one_byte(b: ByteLike) -> bytes:
    if isinstance(b, int):
        if not (0 <= b <= 255):
            raise ValueError("int byte must be in range 0..255")
        return bytes([b])
    if isinstance(b, (bytes, bytearray)) and len(b) == 1:
        return bytes(b)
    raise TypeError("expected a single byte (int or length-1 bytes)")


def _new_ctr(key: bytes, nonce: bytes):
    return Cipher(algorithms.AES(key), modes.CTR(nonce))


# =========================
# בסיס: הצפנת CTR לפי-בייט (ללא אימות)
# =========================

class AESByteEncoder:
    """הצפנה לפי-בייט באמצעות AES-CTR (ללא אימות)."""
    def __init__(self, key: bytes) -> None:
        if not isinstance(key, (bytes, bytearray)):
            raise TypeError("key must be bytes")
        if len(key) not in (16, 24, 32):
            raise ValueError("AES key must be 128/192/256-bit (16/24/32 bytes)")
        self._key = bytes(key)
        self._nonce = urandom(NONCE_LEN)
        self._enc = _new_ctr(self._key, self._nonce).encryptor()
        self._final = False

    @property
    def nonce(self) -> bytes:
        return self._nonce

    def new_message(self, nonce: Optional[bytes] = None) -> None:
        if nonce is None:
            nonce = urandom(NONCE_LEN)
        if not isinstance(nonce, (bytes, bytearray)) or len(nonce) != NONCE_LEN:
            raise ValueError("CTR nonce/IV must be 16 bytes")
        self._nonce = bytes(nonce)
        self._enc = _new_ctr(self._key, self._nonce).encryptor()
        self._final = False

    def encoded(self, one_byte: ByteLike) -> bytes:
        if self._final:
            raise RuntimeError("finalized; call new_message()")
        return self._enc.update(_as_one_byte(one_byte))

    def finalize(self) -> None:
        if not self._final:
            self._enc.finalize()
            self._final = True


class AESByteDecoder:
    """פענוח לפי-בייט (ללא אימות)."""
    def __init__(self, key: bytes) -> None:
        if not isinstance(key, (bytes, bytearray)):
            raise TypeError("key must be bytes")
        if len(key) not in (16, 24, 32):
            raise ValueError("AES key must be 128/192/256-bit")
        self._key = bytes(key)
        self._dec = None
        self._final = False

    def begin(self, nonce: bytes) -> None:
        if not isinstance(nonce, (bytes, bytearray)) or len(nonce) != NONCE_LEN:
            raise ValueError("CTR nonce/IV must be 16 bytes")
        self._dec = _new_ctr(self._key, bytes(nonce)).decryptor()
        self._final = False

    def decoded(self, one_byte: ByteLike) -> bytes:
        if self._dec is None:
            raise RuntimeError("call begin(nonce) first")
        if self._final:
            raise RuntimeError("finalized; call begin(nonce) for a new message")
        return self._dec.update(_as_one_byte(one_byte))

    def finalize(self) -> None:
        if self._dec is not None and not self._final:
            self._dec.finalize()
            self._final = True


# =========================
# גרסת אימות: CTR + HMAC-SHA256
# =========================

class AESByteEncoderAuth:
    """
    הצפנה לפי-בייט + HMAC-SHA256 עבור שלמות/אימות.
    Interface:
      __init__(enc_key, mac_key)
      encoded(b)    -> ciphertext byte
      finalize()    -> returns tag (TAG_LEN bytes)  # tag מעל nonce+ciphertext
      nonce         -> 16 bytes
    """
    def __init__(self, key: bytes, mac_key: bytes) -> None:
        if len(key) not in (16, 24, 32):
            raise ValueError("AES key must be 128/192/256-bit")
        if not isinstance(mac_key, (bytes, bytearray)) or len(mac_key) < 16:
            raise ValueError("mac_key must be bytes (>=16 bytes recommended)")
        self._key = bytes(key)
        self._mac_key = bytes(mac_key)
        self._nonce = urandom(NONCE_LEN)

        self._enc = _new_ctr(self._key, self._nonce).encryptor()
        self._h = hmac.new(self._mac_key, digestmod=hashlib.sha256)
        self._h.update(self._nonce)  # מחייבים שה-tag מכסה את ה-nonce
        self._final = False

    @property
    def nonce(self) -> bytes:
        return self._nonce

    def new_message(self, nonce: Optional[bytes] = None) -> None:
        if nonce is None:
            nonce = urandom(NONCE_LEN)
        if not isinstance(nonce, (bytes, bytearray)) or len(nonce) != NONCE_LEN:
            raise ValueError("CTR nonce/IV must be 16 bytes")
        self._nonce = bytes(nonce)
        self._enc = _new_ctr(self._key, self._nonce).encryptor()
        self._h = hmac.new(self._mac_key, digestmod=hashlib.sha256)
        self._h.update(self._nonce)
        self._final = False

    def encoded(self, one_byte: ByteLike) -> bytes:
        if self._final:
            raise RuntimeError("finalized; call new_message()")
        c = self._enc.update(_as_one_byte(one_byte))
        # מעדכנים HMAC על ה-ciphertext (לא על ה-plaintext)
        self._h.update(c)
        return c

    def finalize(self) -> bytes:
        if not self._final:
            self._enc.finalize()
            tag = self._h.digest()
            self._final = True
            return tag
        raise RuntimeError("already finalized")


class AESByteDecoderAuth:
    """
    פענוח לפי-בייט + אימות HMAC-SHA256.
    שני מצבים:
      mode="stream": מפענח לפי-בייט ומאמת tag רק בסוף (חשיפה ל-on-line tampering עד הסוף).
      mode="buffer":  אינו משחרר plaintext עד אימות tag (בטוח יותר).
    שימוש:
      dec = AESByteDecoderAuth(key, mac_key, mode="buffer"|"stream")
      dec.begin(nonce)
      p = dec.decoded(c)   # ב-stream מחזיר מייד; ב-buffer מאחסן עד verify_tag(...)
      dec.verify_tag(tag)  # חובה לקרוא בסוף; ב-buffer יחזיר את ה-plaintext המצטבר
    """
    def __init__(self, key: bytes, mac_key: bytes, mode: Literal["stream","buffer"]="stream") -> None:
        if len(key) not in (16, 24, 32):
            raise ValueError("AES key must be 128/192/256-bit")
        if not isinstance(mac_key, (bytes, bytearray)) or len(mac_key) < 16:
            raise ValueError("mac_key must be bytes (>=16 bytes recommended)")
        if mode not in ("stream", "buffer"):
            raise ValueError("mode must be 'stream' or 'buffer'")
        self._key = bytes(key)
        self._mac_key = bytes(mac_key)
        self._mode = mode
        self._nonce = None
        self._dec = None
        self._h = None
        self._final = False
        self._buffer_ct = bytearray()
        self._buffer_pt = bytearray()

    def begin(self, nonce: bytes) -> None:
        if not isinstance(nonce, (bytes, bytearray)) or len(nonce) != NONCE_LEN:
            raise ValueError("CTR nonce/IV must be 16 bytes")
        self._nonce = bytes(nonce)
        self._dec = _new_ctr(self._key, self._nonce).decryptor()
        self._h = hmac.new(self._mac_key, digestmod=hashlib.sha256)
        self._h.update(self._nonce)
        self._final = False
        self._buffer_ct.clear()
        self._buffer_pt.clear()

    def decoded(self, one_byte: ByteLike) -> bytes:
        if self._dec is None or self._h is None:
            raise RuntimeError("call begin(nonce) first")
        if self._final:
            raise RuntimeError("already finalized; call begin(nonce) for new message")

        c = _as_one_byte(one_byte)
        # תמיד מעדכנים את HMAC על ה-ciphertext הנכנס
        self._h.update(c)

        if self._mode == "buffer":
            # לא חושפים plaintext עד אימות tag
            self._buffer_ct += c
            p = self._dec.update(c)
            self._buffer_pt += p
            return b""  # לא מחזירים כלום בשלב זה
        else:
            # stream: חושפים מיד
            return self._dec.update(c)

    def verify_tag(self, tag: bytes) -> bytes:
        """מאמת את ה-tag. ב-buffer מחזיר את כל ה-plaintext; ב-stream מחזיר b''."""
        if self._dec is None or self._h is None:
            raise RuntimeError("call begin(nonce) first")
        if self._final:
            raise RuntimeError("already finalized")

        # מסיימים את ה-CTR context
        self._dec.finalize()
        self._final = True

        # מאמתים HMAC
        calc = self._h.digest()
        if not hmac.compare_digest(calc, tag):
            # איפוס חכם למניעת שימוש לא נכון הלאה
            self._buffer_ct.clear()
            self._buffer_pt.clear()
            raise ValueError("HMAC verification failed (ciphertext/nonce corrupted)")

        # ב-buffer: עכשיו אפשר להחזיר את ה-plaintext המצטבר
        if self._mode == "buffer":
            out = bytes(self._buffer_pt)
            self._buffer_ct.clear()
            self._buffer_pt.clear()
            return out
        return b""


if __name__ == "__main__":
    # הדגמת שימוש מלאה
    from os import urandom

    print("[demo] starting per-byte AES-CTR + HMAC demo...")
    key = urandom(32)      # AES-256
    mac_key = urandom(32)  # HMAC-SHA256 key
    message = b"Hello per-byte AES CTR with HMAC!"

    # --- הצפנה לפי-בייט ---
    enc = AESByteEncoderAuth(key, mac_key)
    nonce = enc.nonce
    ct_bytes = bytearray()
    for b in message:
        ct_bytes.append(enc.encoded(b)[0])
    tag = enc.finalize()

    # אריזה לחבילה אחת
    packet = pack_packet(nonce, bytes(ct_bytes), tag)

    # --- פענוח בטוח (buffer-then-verify) ---
    n2, ct2, tag2 = unpack_packet(packet)
    dec_buf = AESByteDecoderAuth(key, mac_key, mode="buffer")
    dec_buf.begin(n2)
    for cb in ct2:
        dec_buf.decoded(cb)
    recovered_buf = dec_buf.verify_tag(tag2)
    assert recovered_buf == message, "buffer mode failed"
    print("[demo] buffer mode OK:", recovered_buf.decode())

    # --- פענוח זרמי (stream + verify בסוף) ---
    dec_stream = AESByteDecoderAuth(key, mac_key, mode="stream")
    dec_stream.begin(nonce)
    recovered_stream = bytearray()
    for cb in ct_bytes:
        recovered_stream += dec_stream.decoded(cb)
    dec_stream.verify_tag(tag)  # יזרוק חריגה אם החבילה נפגמה
    assert bytes(recovered_stream) == message, "stream mode failed"
    print("[demo] stream mode OK:", recovered_stream.decode())

    print("[demo] all good ✅")