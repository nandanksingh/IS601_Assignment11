# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/18/2025
# Assignment-11: Authentication Security Tests (FINAL)
# File: tests/integration/test_auth_security.py
# ----------------------------------------------------------
# Description:
#   • Integration tests for password hashing and JWT utilities
#   • Validates hash/verify functions and token encode/decode
#   • Covers edge cases and monkeypatched failures
# ----------------------------------------------------------

import time
import pytest
import jwt

from app.auth.security import (
    hash_password,
    verify_password,
    verify_password_hash,
    create_access_token,
    decode_access_token,
)
from app.auth.dependencies import SECRET_KEY, ALGORITHM

# ----------------------------------------------------------
# Password Hashing
# ----------------------------------------------------------
def test_password_hashing_and_verification():
    raw = "MyStrongPass123"
    hashed = hash_password(raw)

    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False
    assert verify_password_hash(raw, hashed) is True
    assert verify_password_hash("WrongPassword", hashed) is False

def test_hash_password_invalid_input():
    with pytest.raises(ValueError):
        hash_password("")  # empty string
    with pytest.raises(ValueError):
        hash_password(123)  # non-string

def test_verify_password_invalid_inputs():
    assert verify_password(123, "hash") is False
    assert verify_password("plain", None) is False

# ----------------------------------------------------------
# Token Creation + Decoding
# ----------------------------------------------------------
def test_jwt_create_and_decode():
    payload = {"sub": "123"}
    token = create_access_token(payload)
    decoded = decode_access_token(token)
    assert decoded["sub"] == "123"
    assert "exp" in decoded

def test_create_access_token_failure(monkeypatch):
    monkeypatch.setattr("jwt.encode", lambda *a, **k: (_ for _ in ()).throw(Exception("fail")))
    with pytest.raises(RuntimeError):
        create_access_token({"sub": "x"})

# ----------------------------------------------------------
# Invalid Token
# ----------------------------------------------------------
def test_invalid_token_rejected():
    invalid_token = "this.is.not.valid"
    with pytest.raises(RuntimeError):
        decode_access_token(invalid_token)

# ----------------------------------------------------------
# Expired Token
# ----------------------------------------------------------
def test_expired_token_rejected():
    payload = {"sub": "999", "exp": int(time.time()) - 10}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(RuntimeError):
        decode_access_token(token)

# ----------------------------------------------------------
# Generic Decode Failure
# ----------------------------------------------------------
def test_decode_access_token_generic_failure(monkeypatch):
    monkeypatch.setattr("jwt.decode", lambda *a, **k: (_ for _ in ()).throw(Exception("boom")))
    with pytest.raises(RuntimeError):
        decode_access_token("dummy")

# ----------------------------------------------------------
# Missing 'sub' Field
# ----------------------------------------------------------
def test_token_missing_sub_field():
    token = create_access_token({"foo": "bar"})
    decoded = decode_access_token(token)
    assert decoded.get("sub") is None

# ----------------------------------------------------------
# Custom Claim Integrity
# ----------------------------------------------------------
def test_custom_claim_persists():
    payload = {"sub": "7", "role": "admin"}
    token = create_access_token(payload)
    decoded = decode_access_token(token)
    assert decoded["role"] == "admin"
    assert decoded["sub"] == "7"
