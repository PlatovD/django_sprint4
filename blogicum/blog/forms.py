from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from blog.models import Post, Comment


class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        required=False,
        label="Дата публикации",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image', 'is_published')

    def clean_pub_date(self):
        date = self.cleaned_data['pub_date']
        if not date:
            self.cleaned_data['pub_date'] = timezone.now()
            date = self.cleaned_data['pub_date']
        elif date < timezone.now() - timedelta(minutes=5):
            raise ValidationError('Publication date can not be in past')
        return date


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
