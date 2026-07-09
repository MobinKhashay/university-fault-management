"""
Authentication views: Registration, Email Verification.
Related User Stories: US-01
"""

import random
import string
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from .forms import RegistrationForm, EmailVerificationForm
from .models import User, EmailVerification


def generate_verification_code():
    """Generate a random 6-digit numeric code."""
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(user, code):
    """
    Send verification email with 6-digit code.
    US-01: تایید ایمیل با کد ۶ رقمی
    """
    subject = 'کد تایید ایمیل - سامانه خرابی دانشگاه'
    message = (
        f'سلام {user.first_name} عزیز،\n\n'
        f'کد تایید شما: {code}\n\n'
        f'این کد تا {settings.EMAIL_VERIFICATION_EXPIRY // 60} دقیقه اعتبار دارد.\n\n'
        f'سامانه گزارش و مدیریت خرابی‌های دانشگاه'
    )
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def register_view(request):
    """
    User registration view.
    US-01: ثبت‌نام با نام، نام خانوادگی، نقش، شماره شناسایی، ایمیل، رمز
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # Generate and save verification code
            code = generate_verification_code()
            EmailVerification.objects.create(user=user, code=code)

            # Send verification email
            email_sent = send_verification_email(user, code)

            if email_sent:
                messages.success(request, 'ثبت‌نام با موفقیت انجام شد. کد تایید به ایمیل شما ارسال شد.')
            else:
                messages.warning(
                    request,
                    f'ثبت‌نام انجام شد. ارسال ایمیل با مشکل مواجه شد. کد تایید شما: {code}'
                )

            # Store user id in session for verification
            request.session['verification_user_id'] = user.id

            return redirect('accounts:verify_email')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def verify_email_view(request):
    """
    Email verification view with 6-digit code.
    US-01: تایید ایمیل با کد ۶ رقمی (اعتبار ۱۵ دقیقه)
    """
    user_id = request.session.get('verification_user_id')
    if not user_id:
        messages.error(request, 'لطفاً ابتدا ثبت‌نام کنید.')
        return redirect('accounts:register')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'کاربر یافت نشد.')
        return redirect('accounts:register')

    if user.is_verified:
        messages.info(request, 'ایمیل شما قبلاً تایید شده است.')
        return redirect('accounts:login')

    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']

            # Find valid verification code
            verification = EmailVerification.objects.filter(
                user=user,
                code=code,
                is_used=False,
            ).order_by('-created_at').first()

            if not verification:
                messages.error(request, 'کد تایید نامعتبر است.')
                return render(request, 'accounts/verify_email.html', {
                    'form': form,
                    'email': user.email,
                })

            # Check expiry (15 minutes)
            elapsed = (timezone.now() - verification.created_at).total_seconds()
            if elapsed > settings.EMAIL_VERIFICATION_EXPIRY:
                messages.error(request, 'کد تایید منقضی شده است. لطفاً کد جدید درخواست کنید.')
                return render(request, 'accounts/verify_email.html', {
                    'form': form,
                    'email': user.email,
                })

            # Mark as verified
            verification.is_used = True
            verification.save()
            user.is_verified = True
            user.save()

            # Clear session
            del request.session['verification_user_id']

            messages.success(request, 'ایمیل شما با موفقیت تایید شد. اکنون می‌توانید وارد شوید.')
            return redirect('accounts:login')
    else:
        form = EmailVerificationForm()

    return render(request, 'accounts/verify_email.html', {
        'form': form,
        'email': user.email,
    })


def resend_verification_view(request):
    """
    Resend verification code.
    US-01: ارسال مجدد کد با تایمر ۱۲۰ ثانیه
    """
    user_id = request.session.get('verification_user_id')
    if not user_id:
        return redirect('accounts:register')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('accounts:register')

    # Check rate limiting (max resend per hour)
    recent_codes = EmailVerification.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timezone.timedelta(hours=1),
    ).count()

    if recent_codes >= settings.MAX_PASSWORD_RESET_PER_HOUR:
        messages.error(request, 'تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً بعداً تلاش کنید.')
        return redirect('accounts:verify_email')

    # Generate new code
    code = generate_verification_code()
    EmailVerification.objects.create(user=user, code=code)

    email_sent = send_verification_email(user, code)
    if email_sent:
        messages.success(request, 'کد تایید جدید به ایمیل شما ارسال شد.')
    else:
        messages.warning(request, f'ارسال ایمیل با مشکل مواجه شد. کد تایید شما: {code}')

    return redirect('accounts:verify_email')


def dashboard_redirect_view(request):
    """Redirect user to appropriate dashboard based on role."""
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    if request.user.is_admin_user:
        return redirect('admin_panel:dashboard')
    elif request.user.is_technician:
        return redirect('technicians:dashboard')
    else:
        return redirect('reports:dashboard')
