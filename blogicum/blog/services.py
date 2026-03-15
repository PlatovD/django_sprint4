from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models import Prefetch, prefetch_related_objects
from django.utils import timezone

from blog.managers import PostQueryset
from blog.models import Post, Comment, Category
from blog.utils import OptimizedPaginator

User: AbstractUser = get_user_model()


class PostService:
    @staticmethod
    def get_published_posts_count():
        return (Post.custom_manager.published()
                .only('id')
                .count())

    @staticmethod
    def get_published_posts_count_by_category(category: Category):
        def wrapper():
            return Post.custom_manager.published().filter(category__exact=category).only('id').count()

        return wrapper

    @staticmethod
    def get_all_posts_of_user_count(user: User):
        def wrapper():
            return Post.objects.filter(author__exact=user).only('id').count()

        return wrapper

    @staticmethod
    def get_all_published_posts_of_user_count(user: User):
        def wrapper():
            return PostService.get_published_posts().filter(author__exact=user).only('id').count()

        return wrapper

    @staticmethod
    def get_published_posts() -> PostQueryset:
        return Post.custom_manager.published().with_comment_counts().select_related('author').select_related(
            'location').order_by('-pub_date')

    @staticmethod
    def get_post_details(pk: int, user=None) -> Post | None:
        queryset = Post.objects.select_related('category', 'author', 'location').prefetch_related(
            Prefetch(
                'comments',
                queryset=Comment.objects.select_related('author')
            ))
        post: Post = queryset.filter(pk__exact=pk).first()

        if not post:
            return None
        if post.author == user:
            return post
        if not post.is_published or timezone.now() < post.pub_date:
            return None
        return post

    @staticmethod
    def create_post(instance: Post, user: User):
        if not user:
            raise ValidationError('Post requires author')
        instance.author = user
        return instance


class CategoryService:
    @staticmethod
    def get_published_category_by_slug(slug: str, with_posts=False) -> Category | None:
        query = Category.objects.filter(slug__exact=slug, is_published__exact=True)
        if with_posts:
            query = query.prefetch_related(
                Prefetch('posts', queryset=Post.custom_manager.published().with_comment_counts().select_related(
                    'author').select_related(
                    'location').order_by('-pub_date')))
        return query.first()

    @staticmethod
    def get_category_posts_with_comments_cnt(category: Category):
        if not (hasattr(category, '_prefetched_objects_cache') and 'posts' in category._prefetched_objects_cache):
            prefetch_related_objects([category],
                                     Prefetch('posts',
                                              queryset=Post.custom_manager.published().with_comment_counts().select_related(
                                                  'author').select_related(
                                                  'location').order_by(
                                                  '-pub_date')))
        return category.posts.all()


class CommentService:
    @staticmethod
    def create_comment(instance: Comment, user: User, post):
        if not user:
            raise ValidationError('Comment requires author')
        instance.author = user
        instance.post = post
        return instance


class UserService:
    @staticmethod
    def get_user_profile(username: str, user_made_request: User):
        found_user = User.objects.filter(username__exact=username).first()
        if not found_user:
            return None
        is_profile_owner = user_made_request == found_user
        if is_profile_owner:
            posts_query: PostQueryset = Post.custom_manager.select_related('category').select_related(
                'location').with_comment_counts().order_by('-pub_date')
        else:
            posts_query: PostQueryset = PostService.get_published_posts()

        prefetch_related_objects([found_user], Prefetch('posts', queryset=posts_query))
        return found_user

    @staticmethod
    def get_custom_paginator(queryset, per_page, user, requested_user, **kwargs):
        if user == requested_user:
            return OptimizedPaginator(queryset, per_page, PostService.get_all_posts_of_user_count(user), **kwargs)
        else:
            return OptimizedPaginator(queryset, per_page, PostService.get_all_published_posts_of_user_count(user),
                                      **kwargs)
