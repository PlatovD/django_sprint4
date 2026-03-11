from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

# for future flexable
User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')
