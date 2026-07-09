"""
Registration and authentication forms.
Related User Stories: US-01, US-02, US-03
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import User


class RegistrationForm(forms.ModelForm):
    """
    User registration form.
    Fields change based on selected role (student/professor/staff).
    US-01: نام، نام خانوادگی، نقش، شماره شناسایی، ایمیل، رمز، تکرار رمز، تصویر پروفایل، کارت شناسایی
    """

    password = forms.CharField(
        label='رمز عبور',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'حداقل ۸ کاراکتر',
            'id': 'password',
        })
    )

    password_confirm = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'رمز عبور را تکرار کنید',
            'id': 'password-confirm',
        })
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'role', 'student_id',
            'email', 'phone', 'profile_image', 'id_card_image',
        ]
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'role': 'نقش شما',
            'student_id': 'شماره شناسایی',
            'email': 'ایمیل',
            'phone': 'شماره تلفن',
            'profile_image': 'تصویر پروفایل (اختیاری)',
            'id_card_image': 'تصویر کارت شناسایی',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'نام',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'نام خانوادگی',
            }),
            'role': forms.Select(attrs={
                'class': 'form-input',
                'id': 'role-select',
            }, choices=[
                ('', 'نقش خود را انتخاب کنید'),
                ('student', 'دانشجو'),
                ('professor', 'استاد'),
                ('staff', 'کارمند'),
            ]),
            'student_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'شماره دانشجویی / کارمندی / استادی',
                'id': 'student-id',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'example@urmia.ac.ir',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '09xxxxxxxxx',
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*',
            }),
            'id_card_image': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*',
                'id': 'id-card-input',
            }),
        }

    def clean_email(self):
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('این ایمیل قبلاً ثبت شده است.')
        return email

    def clean_student_id(self):
        """Validate student_id uniqueness."""
        student_id = self.cleaned_data.get('student_id')
        if User.objects.filter(student_id=student_id).exists():
            raise ValidationError('این شماره شناسایی قبلاً ثبت شده است.')
        return student_id

    def clean_phone(self):
        """Validate phone number format."""
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise ValidationError('شماره تلفن باید فقط عدد باشد.')
        if phone and len(phone) != 11:
            raise ValidationError('شماره تلفن باید ۱۱ رقم باشد.')
        return phone

    def clean(self):
        """Validate password match."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'رمز عبور و تکرار آن مطابقت ندارند.')

        return cleaned_data

    def save(self, commit=True):
        """Create user with hashed password."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_verified = False
        if commit:
            user.save()
        return user


class EmailVerificationForm(forms.Form):
    """Form for 6-digit email verification code."""

    code = forms.CharField(
        label='کد تایید',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-input verification-code',
            'placeholder': '------',
            'maxlength': '6',
            'autocomplete': 'off',
            'inputmode': 'numeric',
            'style': 'text-align: center; font-size: 24px; letter-spacing: 12px;',
        })
    )

    def clean_code(self):
        """Validate code is numeric."""
        code = self.cleaned_data.get('code')
        if not code.isdigit():
            raise ValidationError('کد تایید باید فقط عدد باشد.')
        return code


class LoginForm(forms.Form):
    """
    Login form with student_id and password.
    US-02: ورود با شماره شناسایی و رمز عبور + Remember Me
    """

    student_id = forms.CharField(
        label='شماره شناسایی',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'شماره دانشجویی / کارمندی / استادی',
            'autofocus': True,
        })
    )

    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'رمز عبور',
        })
    )

    remember_me = forms.BooleanField(
        label='مرا به خاطر بسپار',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox',
        })
    )


class PasswordResetRequestForm(forms.Form):
    """
    Form to request password reset.
    US-03: ورود ایمیل یا شماره شناسایی برای بازیابی رمز
    """

    identifier = forms.CharField(
        label='ایمیل یا شماره شناسایی',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'ایمیل یا شماره دانشجویی/کارمندی/استادی',
            'autofocus': True,
        })
    )


class PasswordResetCodeForm(forms.Form):
    """
    Form for entering 6-digit reset code.
    US-03: وارد کردن کد ۶ رقمی ارسال شده به ایمیل
    """

    code = forms.CharField(
        label='کد تایید',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-input verification-code',
            'placeholder': '------',
            'maxlength': '6',
            'autocomplete': 'off',
            'inputmode': 'numeric',
            'style': 'text-align: center; font-size: 24px; letter-spacing: 12px;',
        })
    )

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code.isdigit():
            raise ValidationError('کد تایید باید فقط عدد باشد.')
        return code


class PasswordResetNewForm(forms.Form):
    """
    Form for setting new password.
    US-03: رمز جدید + تکرار + چک قوی بودن Real-time
    """

    new_password = forms.CharField(
        label='رمز عبور جدید',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'حداقل ۸ کاراکتر',
            'id': 'new-password',
        })
    )

    confirm_password = forms.CharField(
        label='تکرار رمز عبور جدید',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'رمز عبور جدید را تکرار کنید',
            'id': 'confirm-password',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_pass = cleaned_data.get('new_password')
        confirm = cleaned_data.get('confirm_password')

        if new_pass and confirm and new_pass != confirm:
            self.add_error('confirm_password', 'رمز عبور و تکرار آن مطابقت ندارند.')

        return cleaned_data
