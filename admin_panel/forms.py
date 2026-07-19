"""Admin panel forms. US-04, US-18"""
from django import forms
from django.core.exceptions import ValidationError
from accounts.models import User
from technicians.models import Technician
from reports.models import Specialty

class TechnicianRegistrationForm(forms.Form):
    first_name = forms.CharField(label='نام', max_length=100, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'نام'}))
    last_name = forms.CharField(label='نام خانوادگی', max_length=100, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'نام خانوادگی'}))
    email = forms.EmailField(label='ایمیل', widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'example@urmia.ac.ir'}))
    phone = forms.CharField(label='شماره تماس', max_length=15, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '09xxxxxxxxx'}))
    personnel_code = forms.CharField(label='کد پرسنلی', max_length=20, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'کد پرسنلی'}))
    specialty = forms.ModelChoiceField(label='تخصص', queryset=Specialty.objects.all(), widget=forms.Select(attrs={'class': 'form-input'}))
    shift_start = forms.TimeField(label='شروع شیفت', widget=forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}))
    shift_end = forms.TimeField(label='پایان شیفت', widget=forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}))
    password = forms.CharField(label='رمز عبور', min_length=8, widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'حداقل ۸ کاراکتر'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('این ایمیل قبلاً ثبت شده.')
        return email

    def clean_personnel_code(self):
        code = self.cleaned_data.get('personnel_code')
        if Technician.objects.filter(personnel_code=code).exists():
            raise ValidationError('این کد پرسنلی قبلاً ثبت شده.')
        return code
