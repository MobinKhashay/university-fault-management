"""
User model and authentication-related models.
Related User Stories: US-01, US-02, US-03, US-04
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom manager for User model."""

    def create_user(self, student_id, email, password=None, **extra_fields):
        if not student_id:
            raise ValueError('شماره شناسایی الزامی است.')
        if not email:
            raise ValueError('ایمیل الزامی است.')

        email = self.normalize_email(email)
        user = self.model(student_id=student_id, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, student_id, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_verified', True)
        return self.create_user(student_id, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model supporting three roles:
    - reporter (student/professor/staff)
    - technician
    - admin
    """

    ROLE_CHOICES = [
        ('student', 'دانشجو'),
        ('professor', 'استاد'),
        ('staff', 'کارمند'),
        ('technician', 'تکنسین'),
        ('admin', 'مدیر'),
    ]

    first_name = models.CharField('نام', max_length=100)
    last_name = models.CharField('نام خانوادگی', max_length=100)
    email = models.EmailField('ایمیل', unique=True)
    student_id = models.CharField('شماره شناسایی', max_length=20, unique=True)
    password_hash = models.CharField(max_length=255, blank=True)
    role = models.CharField('نقش', max_length=20, choices=ROLE_CHOICES, default='student')
    profile_image = models.ImageField('تصویر پروفایل', upload_to='profiles/', blank=True, null=True)
    phone = models.CharField('شماره تلفن', max_length=15, blank=True)
    id_card_image = models.ImageField('تصویر کارت شناسایی', upload_to='id_cards/', blank=True, null=True)
    is_verified = models.BooleanField('تایید شده', default=False)
    is_id_verified = models.BooleanField(default=False, verbose_name='هویت تایید شده')
    is_active = models.BooleanField('فعال', default=True)
    is_staff = models.BooleanField('دسترسی ادمین', default=False)
    created_at = models.DateTimeField('تاریخ ثبت‌نام', default=timezone.now)

    # Rate limiting fields
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    ip_lock_count = models.PositiveIntegerField(default=0)

    objects = UserManager()

    USERNAME_FIELD = 'student_id'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"

    @property
    def is_reporter(self):
        return self.role in ('student', 'professor', 'staff')

    @property
    def is_technician(self):
        return self.role == 'technician'

    @property
    def is_admin_user(self):
        return self.role == 'admin'

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class EmailVerification(models.Model):
    """Stores email verification codes for registration."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications')
    code = models.CharField('کد تایید', max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'تایید ایمیل'
        ordering = ['-created_at']

    def __str__(self):
        return f"Code for {self.user.email}"


class PasswordResetToken(models.Model):
    """
    Stores secure one-time tokens for password recovery.
    Related to US-03 security flow.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField('توکن', max_length=64, unique=True)
    code = models.CharField('کد تایید', max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'توکن بازیابی رمز'
        ordering = ['-created_at']

    def __str__(self):
        return f"Reset token for {self.user.email}"
