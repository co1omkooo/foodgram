from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from footgram_backend.constans import MAX_LENGTH_EMAIL, MAX_LENGTH_USER_NAME


class User(AbstractUser):

    REQUIRED_FIELDS = ['first_name', 'last_name', 'username', 'password']
    USERNAME_FIELD = 'email'

    username = models.CharField(
        max_length=MAX_LENGTH_USER_NAME,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        verbose_name='Имя пользователя',
        error_messages={
            'unique': 'Пользователь с таким именем уже зарегистрирован',
        },
    )
    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        blank=False,
        verbose_name='Электронная почта',
        error_messages={
            'unique': 'Пользователь с таким адресом уже зарегистрирован',
        },
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_USER_NAME,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_USER_NAME,
        verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        upload_to='users/',
        null=True,
        blank=True,
        verbose_name='Аватар',
    )

    class Meta:
        ordering = ['username']
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_to',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                name='unique_subscription',
                fields=['user', 'author']
            )
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
