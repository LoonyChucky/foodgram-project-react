import json

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient, Tag


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        ingredients_file = open(
            f'{settings.BASE_DIR}/data/ingredients.json',
            encoding='utf-8')
        try:
            ingredients_data = json.load(ingredients_file)
            for item in ingredients_data:
                Ingredient.objects.get_or_create(**item)
        except FileNotFoundError:
            raise CommandError('Ingredients file not found')
        finally:
            ingredients_file.close()

        print('Ingredients uploaded')

        tags_file = open(
            f'{settings.BASE_DIR}/data/tags.json',
            encoding='utf-8')
        try:
            tags_data = json.load(tags_file)
            for item in tags_data:
                Tag.objects.get_or_create(**item)
        except FileNotFoundError:
            raise CommandError('Tags file not found')
        finally:
            tags_file.close()

        print('Tags uploaded')
