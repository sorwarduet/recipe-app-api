from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Ingredient
from .serializers import TagSerializer, IngredientSerializer
# Create your views here.


class BasicRecipeAttrViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    """Base view set for user"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return only user login object"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create new object"""
        serializer.save(user=self.request.user)


class TagViewSet(BasicRecipeAttrViewSet):
    """Manage the tag database"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(BasicRecipeAttrViewSet):
    """Create Ingredient views"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
