from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User

MIN_VALUE = 1
MAX_VALUE = 32000


class Tag(models.Model):

    name = models.CharField(
        'Tag',
        max_length=200,
        unique=True,
        blank=False,
    )

    slug = models.SlugField(
        'Slug',
        max_length=200,
        unique=True,
        blank=False,
    )

    color = ColorField(
        'Tag color',
        max_length=7,
        unique=True,
        blank=False,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        'Ingredient',
        max_length=200,
        blank=False,
    )

    measurement_unit = models.CharField(
        'Measurement Unit',
        max_length=200,
        blank=False,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient_unit'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):

    name = models.CharField(
        'Recipe',
        max_length=200,
        blank=False
    )

    text = models.TextField(
        'Recipe discription',
        blank=False,
    )

    image = models.ImageField(
        'Picture',
        upload_to='recipes/images/',
        blank=False,
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Tags',
        related_name='recipes',
        blank=False,
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ingredients',
        related_name='recipes',
        through='IngredientAmount',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Recipe author',
    )

    cooking_time = models.PositiveSmallIntegerField(
        'Cooking time',
        validators=[
            MinValueValidator(limit_value=MIN_VALUE,
                              message=f'At least {MIN_VALUE} minute!'),
            MaxValueValidator(limit_value=MAX_VALUE,
                              message=f'No more than {MAX_VALUE} minutes!'),
        ],
    )

    pub_date = models.DateTimeField(
        'Publication date',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self) -> str:
        return f'{self.name}'


class IngredientAmount(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe',
        related_name='recipe_ingredient',
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ingredient',
        related_name='recipe_ingredient',
    )

    amount = models.PositiveSmallIntegerField(
        'Ingredient amount',
        validators=(
            MinValueValidator(MIN_VALUE, f'Minimum {MIN_VALUE} unit'),
            MaxValueValidator(MAX_VALUE, f'Max {MAX_VALUE} units'),
        ),
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Ingredient in recipe'
        verbose_name_plural = 'Ingredients in recipe'

    def __str__(self):
        return (f'{self.ingredient.name} {self.amount} '
                f'{self.ingredient.measurement_unit}')


class Favorite(models.Model):

    user = models.ForeignKey(
        User,
        verbose_name='User',
        on_delete=models.CASCADE,
        related_name='recipes_favorite_related',
    )

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Recipe',
        on_delete=models.CASCADE,
        related_name='recipes_favorite_related',
    )

    date_added = models.DateTimeField(
        'Add date',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        ordering = ('-date_added',)
        verbose_name = 'Favorite recipe'
        verbose_name_plural = 'Favorite recipes'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name=('recipe already'
                      ' in user\'s favorites'),
            ),
        )

    def __str__(self):
        return f' {self.recipe} to Favorites'


class ShoppingCart(models.Model):

    user = models.ForeignKey(
        User,
        verbose_name='User',
        on_delete=models.CASCADE,
        related_name='recipes_shoppingcart_related',
    )

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Recipe',
        on_delete=models.CASCADE,
        related_name='recipes_shoppingcart_related',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Recipe in shopping cart'
        verbose_name_plural = 'Recipes in shopping cart'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name=('recipe already'
                      ' in user\'s cart'),
            ),
        )

    def __str__(self):
        return f'{self.recipe} added shopping cart'
