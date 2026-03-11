from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import prefetch_related_objects, Prefetch
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, UpdateView

from blog.models import Post
from users.forms import CustomUserCreationForm

User = get_user_model()


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
        if queryset is None:
            queryset = self.get_queryset()

        obj: User = super().get_object(queryset=queryset)
        if self.request.user and obj == self.request.user:
            prefetch_related_objects([obj], 'posts')
        else:
            prefetch_related_objects(
                [obj],
                Prefetch('posts',
                         queryset=
                         Post.objects.filter(is_published__exact=True, pub_date__lte=timezone.now()))
            )
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context.get('profile'):
            posts = context.get('profile').posts.order_by('pub_date').all()
            paginator = Paginator(posts, 10)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context.update({'page_obj': page_obj})
        return context


class CustomLoginView(LoginView):
    def get_success_url(self):
        return reverse('profile', kwargs={'username': self.request.user.username})


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user
