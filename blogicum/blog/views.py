from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from blog.forms import PostForm, CommentForm, CustomUserCreationForm
from blog.models import Post, Comment
from blog.services import PostService, CategoryService, CommentService, UserService
from blog.utils import OptimizedPaginator

User = get_user_model()


class IndexView(ListView):
    template_name = 'blog/index.html'
    paginate_by = 10
    context_object_name = 'post_list'

    def get_queryset(self):
        return PostService.get_published_posts()

    def get_paginator(self, queryset, per_page, orphans=0,
                      allow_empty_first_page=True, **kwargs):
        return OptimizedPaginator(
            queryset,
            per_page,
            count_func=PostService.get_published_posts_count,
            orphans=orphans,
            allow_empty_first_page=allow_empty_first_page,
            **kwargs
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = PostService.get_post_details(self.kwargs.get('post_id'), self.request.user)
        if not post:
            raise Http404('Post not found')
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'form': CommentForm(),
            'comments': self.object.comments.all()
        })
        return context


class PostActionMixin(LoginRequiredMixin, UserPassesTestMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class PostUpdateView(PostActionMixin, UpdateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user == self.get_object().author

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class PostDeleteView(PostActionMixin, DeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'form': PostForm(instance=self.get_object())
        })
        return context

    def test_func(self):
        return self.request.user == self.get_object().author

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])

    def get_success_url(self):
        return reverse_lazy('blog:index')


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        category = CategoryService.get_published_category_by_slug(self.kwargs.get('category_slug'), with_posts=True)
        if not category:
            raise Http404('Category was not found')
        self.category = category
        return CategoryService.get_category_posts_with_comments_cnt(category)

    def get_paginator(self, queryset, per_page, orphans=0,
                      allow_empty_first_page=True, **kwargs):
        return OptimizedPaginator(
            queryset,
            per_page,
            count_func=PostService.get_published_posts_count_by_category(self.category),
            orphans=orphans,
            allow_empty_first_page=allow_empty_first_page,
            **kwargs
        )

    def get_context_data(self, *, object_list: list[Post] = None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context.update({
            'category': self.category
        })
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        form.instance = PostService.create_post(form.instance, self.request.user)
        return super().form_valid(form)


class CommentCreateView(LoginRequiredMixin, CreateView):
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def form_valid(self, form):
        post = PostService.get_post_details(self.kwargs.get('post_id'), user=self.request.user)
        if not post:
            raise Http404('Post for commenting not found')
        form.instance = CommentService.create_comment(form.instance, self.request.user, post)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class CommentUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class CommentDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class UserCreateView(CreateView):
    model = User
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('blog:index')
    form_class = CustomUserCreationForm


class UserProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        profile = UserService.get_user_profile(self.kwargs.get('username'), self.request.user)
        if not profile:
            raise Http404('Profile not found')
        return profile

    def get_paginator_custom(self, queryset, per_page, user, requested_user, **kwargs) -> Paginator:
        return UserService.get_custom_paginator(queryset, per_page, user, requested_user, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        posts = profile.posts.all()
        paginator = self.get_paginator_custom(posts, 10, profile, self.request.user)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context.update({
            'page_obj': page_obj
        })
        return context


class CustomLoginView(LoginView):
    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:index')

    fields = ('username', 'first_name', 'last_name')
