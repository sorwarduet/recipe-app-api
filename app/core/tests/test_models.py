from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email='test@test.com', password='testpass'):
    """Create the sample user for test"""
    return get_user_model().objects.create_user(email,password)

class ModelTests(TestCase):

    def test_user_with_email_successful(self):
        """Test creating new user with email and password"""

        email = "test@gmail.com"
        password = "TestPass1234"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_is_normalized(self):

        """Email normalized """

        email = 'test@GAMIL.Com'
        password = "TestPass1234"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')


    def test_new_super_user(self):
        """Create super user"""
        user = get_user_model().objects.create_superuser(
            'test@gmail.com',
            'test12345'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Apple'
        )
        self.assertEqual(str(tag), tag.name)



