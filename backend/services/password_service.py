
import bcrypt


def hash_password(password):
    """Convert a plain-text password into a secure bcrypt hash."""

    password_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(password_bytes, salt)

    return hashed_password.decode("utf-8")


def verify_password(password, stored_hash):
    """Verify a password against its stored bcrypt hash."""

    password_bytes = password.encode("utf-8")
    hash_bytes = stored_hash.encode("utf-8")

    return bcrypt.checkpw(password_bytes, hash_bytes)
