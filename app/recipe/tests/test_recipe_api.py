from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.conf import settings

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return the detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Sample Tag'):
    """Create the Tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Sample Tag'):
    """Create the Tag"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """Create the sample recipe"""
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeTestApi(TestCase):
    """Test the public Api access"""

    def setUp(self):
        self.client = APIClient()

    def test_recipe_required(self):
        """Test the login required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeTestApi(TestCase):
    """Test private recipe API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='testpass'
        )
        self.client.force_authenticate(self.user)

    def test_recipe_retrieve(self):
        """Test the retrieve all recipe"""

        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializers = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializers.data)

    def test_recipe_limited_user(self):
        """Test limited access"""

        user2 = get_user_model().objects.create_user(
            email='notest@test.com',
            password='testpass'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_detail(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)

        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_basic_recipe(self):
        """Test Basic Recipe"""
        payload = {
            'title': 'Choclte Test',
            'time_minutes': 5,
            'price': 5.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Create the recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Desert')

        payload = {
            'title': 'Test Recipe',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 5,
            'price': 5.00
        }
        res = self.client.post(RECIPES_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredient(self):
        """Create the recipe with ingredient"""
        ing1 = sample_ingredient(user=self.user, name='Pawser')
        ing2 = sample_ingredient(user=self.user, name='Toalt')

        payload = {
            'title': 'Test Recipe',
            'ingredients': [ing1.id, ing2.id],
            'time_minutes': 5,
            'price': 5.00
        }

        res = self.client.post(RECIPES_URL, payload)

        recipe = Recipe.objects.get(id=res.data['id'])
        ings = recipe.ingredients.all()
        self.assertEqual(ings.count(), 2)
        self.assertIn(ing1, ings)
        self.assertIn(ing1, ings)

    def test_partial_recipe_update(self):
        """Test the update"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(self.user, name='Curry')
        payload = {'title': 'New Recipe', 'tags': [new_tag.id]}

        url = detail_url(recipe.id)

        res = self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 1)















