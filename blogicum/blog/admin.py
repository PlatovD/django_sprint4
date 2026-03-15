from django.contrib import admin
from blog.models import Category, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'created_at'
    )
    search_fields = (
        'title',
        'slug',
    )
    list_display_links = ('title', 'slug')
    empty_value_display = 'Не задано'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )
    search_fields = (
        'name',
    )
    list_display_links = ('name',)
    empty_value_display = 'Не задано'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'is_published',
        'created_at'
    )
    search_fields = (
        'title',
    )
    list_display_links = ('title',)
    empty_value_display = 'Не задано'
