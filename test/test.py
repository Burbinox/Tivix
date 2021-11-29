import unittest
from utils import hash_password, create_session_token
from freezegun import freeze_time


class UnitTest(unittest.TestCase):
    def test_hash_password(self):
        expected_output = "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92"
        self.assertEqual(hash_password(123, 456), expected_output)
        expected_output = "d597ec7a020e32067c82eb584f8b24c0b65f9769390b3bf452c76e496a976a5c"
        self.assertEqual(hash_password(123, "śćź"), expected_output)

    @freeze_time("2020-01-01")
    def test_create_session_token(self):
        expected_output = "92a28ffd7e233ffd6ef9ce1a10b0fdd273ec22e0bc5784959475ea506179ce2b"
        self.assertEqual(create_session_token(123), expected_output)

