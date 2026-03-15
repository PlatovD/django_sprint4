from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from blog.models import Post, Comment

MAX_PAST_MINUTES = 5
User = get_user_model()


class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        required=False,
        label="Дата публикации",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image', 'is_published')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')
