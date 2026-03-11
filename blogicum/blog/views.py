from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from blog.forms import PostForm, CommentForm
from blog.models import Post, Category, Comment


class IndexView(ListView):
    template_name = 'blog/index.html'
    paginate_by = 10
    context_object_name = 'post_list'

    def get_queryset(self):
        return get_published_posts()


def get_published_posts():
    return Post.objects.select_related('category').annotate(comment_count=Count('comments')).filter(
        Q(is_published__exact=True)
        & Q(pub_date__lte=timezone.now())
        & Q(category__is_published=True))


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        queryset = (Post.objects
                    .filter(
            is_published__exact=True,
            category__is_published__exact=True,
            pub_date__lte=timezone.now()
        )
                    .select_related('category', 'author', 'location')
                    .prefetch_related('comments'))
        self.post = get_object_or_404(queryset, pk=self.kwargs.get(self.pk_url_kwarg))
        return self.post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.post.comments.select_related('author').all()
        return context


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        slug = self.kwargs.get('category_slug')
        category_requested = get_object_or_404(Category, slug__exact=slug)
        if not category_requested.is_published:
            raise Http404('Category was not found')
        self.category_requested = category_requested
        return (category_requested.posts.filter(is_published__exact=True, pub_date__lte=timezone.now()).order_by(
            'pub_date'))

    def get_context_data(self, *, object_list: list[Post] = None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['category'] = self.category_requested
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('profile', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


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
        return redirect('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class PostDeleteView(PostActionMixin, DeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse('blog:index')

    def test_func(self):
        return self.request.user == self.get_object().author

    def handle_no_permission(self):
        return redirect('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class CommentCreateView(LoginRequiredMixin, CreateView):
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def form_valid(self, form):
        obj = form.instance
        obj.author = self.request.user
        obj.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class CommentUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class CommentDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})
