"""Profile and password change forms. US-10"""
from django import forms
from accounts.models import User

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'phone', 'profile_image']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-input'}),
        }

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='رمز فعلی', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password = forms.CharField(label='رمز جدید', min_length=8, widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    confirm_password = forms.CharField(label='تکرار رمز جدید', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
