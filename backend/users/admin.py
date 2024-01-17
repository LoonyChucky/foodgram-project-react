from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import Subscription, User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
    )

    list_filter = ('email', 'username',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    list_filter = ('id', 'user', 'author')
