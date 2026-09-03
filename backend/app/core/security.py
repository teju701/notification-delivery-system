import secrets
import hashlib


def generate_api_key(prefix: str = "nds_live_") -> tuple[str, str]:
    """
    Generates a secure API key and its SHA-256 hash.
    Returns (raw_key, hashed_key).
    Raw key is given once to user; hashed_key is stored in DB.
    """
    token = secrets.token_hex(24)
    raw_key = f"{prefix}{token}"
    hashed_key = hash_api_key(raw_key)
    return raw_key, hashed_key


def hash_api_key(api_key: str) -> str:
    """Computes SHA-256 hash of API key for secure DB comparison."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()
