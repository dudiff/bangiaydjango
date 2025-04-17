from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User, Profile
from shipping.models import City, District, Ward 

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên đăng nhập'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Nhập email'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nhập lại password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        
class UserLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập email hoặc tên đăng nhập'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mật khẩu'})
    )
class UserProfileForm(forms.ModelForm):
    # bio = forms.CharField(
    #     widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tiểu sử'}),
    #     required=False
    # )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tiểu sử', 'rows': 3}),
        }
