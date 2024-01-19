from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeListSerializer, RecipeSerializer,
                             ShoppingCartSerializer, TagSerializer)
from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from utils.filters import IngredientFilter, RecipeFilter
from utils.paginations import CustomPagination
from utils.permissions import IsAuthorOrReadOnly


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'ingredients')
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeSerializer

    @action(methods=['post'],
            detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        serializer = ShoppingCartSerializer(
            data={'user': request.user.id, 'recipe': pk},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        recipe = Recipe.objects.filter(id=pk)
        if not recipe.exists():
            return Response({'error': 'no such recipe'},
                            status=status.HTTP_404_NOT_FOUND)

        instance = request.user.recipes_shoppingcart_related.filter(
            recipe_id=pk)
        if instance.exists():
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'error': 'no such recipe'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'],
            detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        shopping_cart = self.request.user.recipes_shoppingcart_related.all()
        recipes = [item.recipe.id for item in shopping_cart]
        shopping_list = IngredientAmount.objects.filter(
            recipe__in=recipes).values('ingredient').annotate(
            amount=Sum('amount'))

        shopping_list_text = 'Список покупок:\n\n'

        for item in shopping_list:
            ingredient = Ingredient.objects.get(pk=item['ingredient'])
            amount = item['amount']
            shopping_list_text += (f'{ingredient.name}, {amount} '
                                   f'{ingredient.measurement_unit}\n')

        response = HttpResponse(shopping_list_text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=shopping_list.txt')

        return response

    @action(methods=['post'],
            detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        serializer = FavoriteSerializer(
            data={'user': request.user.id, 'recipe': pk},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        recipe = Recipe.objects.filter(id=pk)
        if not recipe.exists():
            return Response({'error': 'no such recipe'},
                            status=status.HTTP_404_NOT_FOUND)

        instance = request.user.recipes_favorite_related.filter(recipe=pk)

        if instance.exists():
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'error': 'no such recipe'},
            status=status.HTTP_400_BAD_REQUEST)
