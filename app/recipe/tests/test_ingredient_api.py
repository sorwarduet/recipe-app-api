from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Ingredient
from ..serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientTest(TestCase):
    """Test publicly available ingredient Api """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access endpoint"""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientTest(TestCase):
    """Test private ingredient API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'passtest'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test the retrieve ingredient list"""

        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_user(self):
        """Test limited access"""

        user2 = get_user_model().objects.create_user(
            email='notest@test.com',
            password='testpass'
        )
        Ingredient.objects.create(user=user2, name='Fruity')
        ingredient = Ingredient.objects.create(user=self.user, name='Vegetable')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_ingredient_create_successful(self):
        """Tag create successfull"""

        payload = {'name': 'Test Ingreident'}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_ingredient_create_invalid(self):
        """Test the invalid name"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)



