from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models import Prefetch, QuerySet, prefetch_related_objects
from django.utils import timezone

from blog.managers import PostQueryset
from blog.models import Post, Comment, Category

User: AbstractUser = get_user_model()


class PostService:
    @staticmethod
    def get_published_posts() -> PostQueryset:
        return Post.custom_manager.published().select_related('category').with_comment_counts().order_by('-pub_date')

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
                Prefetch('posts', queryset=Post.custom_manager.published().order_by('-pub_date')))
        return query.first()


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
            posts_query: PostQueryset = Post.custom_manager.order_by('-pub_date')
        else:
            posts_query: PostQueryset = PostService.get_published_posts()

        posts_query = posts_query.with_comment_counts()
        prefetch_related_objects([found_user], Prefetch('posts', queryset=posts_query))
        return found_user
