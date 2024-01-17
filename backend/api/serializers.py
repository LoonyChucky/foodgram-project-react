from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientAmountSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), )
    amount = serializers.IntegerField(
        min_value=1,
        max_value=10000)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class CustomUserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.followed_users.filter(author=obj).exists()
        return False


class SubscriberSerializer(CustomUserSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(CustomUserSerializer.Meta):
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')

        read_only_fields = ('email',
                            'username',
                            'first_name',
                            'last_name')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user

        if Subscription.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(
                'You are already subscribed to this user!')

        if user == author:
            raise serializers.ValidationError(
                'You cannot subscribe to yourself')

        return data

    def get_recipes(self, obj):
        queryset = obj.recipes.all()
        recipes_limit = self.context['request'].GET.get('recipes_limit')

        if recipes_limit and recipes_limit.isdigit():
            queryset = queryset[: int(recipes_limit)]

        recipes = BriefRecipeSerializer(
            queryset, many=True,
            context=self.context)

        return recipes.data


class CreateSubscribtionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def validate(self, data):
        user = data.get('user').id
        author = data.get('author').id

        if Subscription.objects.filter(
                author=author, user=user).exists():
            raise serializers.ValidationError(
                detail='already subscribed',
                code=status.HTTP_400_BAD_REQUEST)

        if user == author:
            raise serializers.ValidationError(
                detail='can\'t subscribe to yourself',
                code=status.HTTP_400_BAD_REQUEST)

        return data

    def to_representation(self, instance):
        return SubscriberSerializer(
            instance=instance.author,
            context=self.context).data


class BriefRecipeSerializer(serializers.ModelSerializer):

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data.get('user').id
        recipe = data.get('recipe').id
        if self.Meta.model.objects.filter(user=user,
                                          recipe=recipe).exists():
            raise serializers.ValidationError('Recipe already in favorite')
        return data

    def to_representation(self, instance):
        serializer = BriefRecipeSerializer(
            instance.recipe, context=self.context)
        return serializer.data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data.get('user').id
        recipe = data.get('recipe').id
        if self.Meta.model.objects.filter(user=user,
                                          recipe=recipe).exists():
            raise serializers.ValidationError('Recipe already in cart')
        return data

    def to_representation(self, instance):
        serializer = BriefRecipeSerializer(
            instance.recipe, context=self.context)
        return serializer.data


class RecipeListSerializer(serializers.ModelSerializer):

    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True,
        source='recipe_ingredient')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'text',
                  'author',
                  'image',
                  'tags',
                  'ingredients',
                  'cooking_time',
                  'is_favorited',
                  'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return getattr(user, 'recipes_favorite_related'
                           ).filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return getattr(user, 'recipes_shoppingcart_related'
                           ).filter(recipe=obj).exists()
        return False


class RecipeSerializer(serializers.ModelSerializer):

    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=1, error_messages={'min_value': 'At least 1 minute'})
    ingredients = AddIngredientAmountSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'text',
                  'author',
                  'image',
                  'tags',
                  'ingredients',
                  'cooking_time')

    def validate(self, data):
        cooking_time = data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                details='Cooking time must be more than 0 min',
                code=status.HTTP_400_BAD_REQUEST)

        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                detail='must have ingredients',
                code=status.HTTP_400_BAD_REQUEST)

        ingredient_ids = [item['id'] for item in ingredients]
        if len(set(ingredient_ids)) != len(ingredients):
            raise serializers.ValidationError(
                detail='ingredients should not repeat',
                code=status.HTTP_400_BAD_REQUEST)

        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                detail='must have tags',
                code=status.HTTP_400_BAD_REQUEST)

        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                detail='tags should not repeat',
                code=status.HTTP_400_BAD_REQUEST)

        image = data.get('image')
        if not image:
            raise serializers.ValidationError(
                detail='must have image',
                code=status.HTTP_400_BAD_REQUEST)

        return data

    @staticmethod
    def create_ingredients(recipe, ingredients):
        create_ingredients = [IngredientAmount(
                recipe=recipe, ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients]
        IngredientAmount.objects.bulk_create(create_ingredients)

    def create(self, validated_data):
        user = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data, author=user)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(validated_data.pop('tags'))
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, recipe):
        return RecipeListSerializer(recipe, context=self.context).data
