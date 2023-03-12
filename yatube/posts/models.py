from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Название группы',
        max_length=200,
    )
    slug = models.SlugField(
        'Уникальная часть URL группы',
        unique=True,
    )
    description = models.TextField(
        'Описание группы',
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self) -> str:
        return self.title[:settings.MAX_GROUP_SELF_TEXT_LENGTH]


class Post(models.Model):
    text = models.TextField(
        'Содержание записи',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Группа'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.text[:settings.MAX_POST_SELF_TEXT_LENGTH]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        blank=False,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Запись'
    )
    text = models.TextField(
        'Содержание комментария',
    )
    created = models.DateTimeField(
        'Дата комментария',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-created',)

    def __str__(self) -> str:
        return self.text[:settings.MAX_COMMENT_SELF_TEXT_LENGTH]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    author = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return ('Подписки '
                + self.user.username
                )[:settings.MAX_FOLLOW_SELF_TEXT_LENGTH]
