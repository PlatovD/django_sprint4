from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

from blog.managers import PostManager

User = get_user_model()


class BaseModel(models.Model):
    is_published = (models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Добавлено'
    )
    objects = models.Manager()

    class Meta:
        abstract = True

    def __str__(self):
        return "abstract model"


class Category(BaseModel):
    title = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Заголовок'
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True, blank=False, verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; разрешены символы'
                  ' латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(
        max_length=256,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(BaseModel):
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок'
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем'
                  ' — можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name='Автор публикации',
        related_name='posts')
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Местоположение',
        related_name='posts')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        verbose_name='Категория',
        related_name='posts'
    )
    image = models.ImageField(
        'Изображение',
        blank=True,
        upload_to='blog_images'
    )

    custom_manager = PostManager()

    def get_post_with_all_data(self):
        return

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class Comment(BaseModel):
    text = models.TextField(
        'Текст комментария',
        blank=False,
        null=False
    )
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        verbose_name = 'комментарий к публикации'
        verbose_name_plural = 'комментарии к публикациям'
        ordering = ('created_at',)

    def __str__(self):
        # в принципе если проект небольшой то сильно не нагрузит админку
        return f'{"".join(self.text.split()[:3])}... - {self.author.username}'
