from django.contrib import admin

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)


class IngredientInlineAdmin(admin.StackedInline):

    model = IngredientAmount
    autocomplete_fields = ('ingredient',)
    min_num = 1


@admin.register(IngredientAmount)
class AmountIngredientAdmin(admin.ModelAdmin):

    list_display = ('recipe', 'ingredient', 'amount',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = ('name', 'slug', 'color',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):

    list_display = ('user', 'recipe',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):

    list_display = ('user', 'recipe',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'pub_date',
        'display_ingredients',
        'display_favorites_count',
    )

    list_filter = ('name', 'author__username', 'tags__name')
    inlines = (IngredientInlineAdmin,)

    @admin.display(description='Ingredients')
    def display_ingredients(self, obj):
        ingredients_list = [
            ingredient.name for ingredient in obj.ingredients.all()]
        if ingredients_list:
            return ', '.join(ingredients_list)
        return '-'

    @admin.display(description='In favorites')
    def display_favorites_count(self, obj):
        return obj.recipes_favorite_related.count()
