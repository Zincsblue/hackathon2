"""
Password hashing and verification service using Argon2id.
Provides secure password handling with industry-standard parameters.
"""
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class PasswordService:
    """
    Password hashing service using Argon2id algorithm.
    Argon2id is recommended by OWASP for password hashing.
    """

    def __init__(self):
        """Initialize Argon2 password hasher with secure defaults."""
        self.hasher = PasswordHasher(
            time_cost=2,  # Number of iterations
            memory_cost=65536,  # Memory usage in KiB (64 MB)
            parallelism=4,  # Number of parallel threads
            hash_len=32,  # Length of hash in bytes
            salt_len=16,  # Length of salt in bytes
        )

    def hash_password(self, password: str) -> str:
        """
        Hash a password using Argon2id.

        Args:
            password: Plain text password to hash

        Returns:
            Hashed password string
        """
        return self.hasher.hash(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password to verify
            password_hash: Hashed password to verify against

        Returns:
            True if password matches, False otherwise
        """
        try:
            self.hasher.verify(password_hash, password)
            return True
        except VerifyMismatchError:
            return False

    def needs_rehash(self, password_hash: str) -> bool:
        """
        Check if a password hash needs to be rehashed with updated parameters.

        Args:
            password_hash: Hashed password to check

        Returns:
            True if rehashing is recommended, False otherwise
        """
        return self.hasher.check_needs_rehash(password_hash)


# Singleton instance
password_service = PasswordService()
