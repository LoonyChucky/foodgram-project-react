from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
from django.db import models


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',
                       'password',
                       'first_name',
                       'last_name')

    username = models.CharField(
        'Username',
        max_length=149,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9]+([_.-]?[a-zA-Z0-9])*$')],
    )

    email = models.EmailField(
        'User email',
        max_length=254,
        unique=True,
        blank=False,
        validators=[EmailValidator],
    )

    first_name = models.CharField(
        'User first name',
        max_length=149,
        blank=False,
    )

    last_name = models.CharField(
        'User last name',
        max_length=149,
        blank=False,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return f'{self.username}: {self.email}'


class Subscription(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followed_users',
        verbose_name='Follower',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Author',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name=(
                    'cannot subscribe '
                    'to same author twice\n'),
            ),
        )

    def __str__(self):
        return f'User {self.user} subscribed to {self.author}'

    def save(self, *args, **kwargs):
        if self.user == self.author:
            raise ValidationError('You cannot subscribe to yourself')
        super().save(*args, **kwargs)
