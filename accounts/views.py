"""
Authentication views: Registration, Email Verification, Login, Logout.
Related User Stories: US-01, US-02
"""

import random
import string
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from .forms import RegistrationForm, EmailVerificationForm, LoginForm
from .models import User, EmailVerification


# ============================================================
# Helper Functions
# ============================================================

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


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def generate_captcha():
    """Generate simple math captcha. Returns (question, answer)."""
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    return f"{a} + {b}", str(a + b)


# ============================================================
# Registration Views (US-01)
# ============================================================

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

            verification = EmailVerification.objects.filter(
                user=user, code=code, is_used=False,
            ).order_by('-created_at').first()

            if not verification:
                messages.error(request, 'کد تایید نامعتبر است.')
                return render(request, 'accounts/verify_email.html', {
                    'form': form, 'email': user.email,
                })

            # Check expiry (15 minutes)
            elapsed = (timezone.now() - verification.created_at).total_seconds()
            if elapsed > settings.EMAIL_VERIFICATION_EXPIRY:
                messages.error(request, 'کد تایید منقضی شده است. لطفاً کد جدید درخواست کنید.')
                return render(request, 'accounts/verify_email.html', {
                    'form': form, 'email': user.email,
                })

            # Mark as verified
            verification.is_used = True
            verification.save()
            user.is_verified = True
            user.save()

            del request.session['verification_user_id']
            messages.success(request, 'ایمیل شما با موفقیت تایید شد. اکنون می‌توانید وارد شوید.')
            return redirect('accounts:login')
    else:
        form = EmailVerificationForm()

    return render(request, 'accounts/verify_email.html', {
        'form': form, 'email': user.email,
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

    recent_codes = EmailVerification.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timezone.timedelta(hours=1),
    ).count()

    if recent_codes >= settings.MAX_PASSWORD_RESET_PER_HOUR:
        messages.error(request, 'تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً بعداً تلاش کنید.')
        return redirect('accounts:verify_email')

    code = generate_verification_code()
    EmailVerification.objects.create(user=user, code=code)

    email_sent = send_verification_email(user, code)
    if email_sent:
        messages.success(request, 'کد تایید جدید به ایمیل شما ارسال شد.')
    else:
        messages.warning(request, f'ارسال ایمیل با مشکل مواجه شد. کد تایید شما: {code}')

    return redirect('accounts:verify_email')


# ============================================================
# Login & Logout Views (US-02)
# ============================================================

def login_view(request):
    """
    User login view with security features.
    US-02: ورود با شماره شناسایی و رمز عبور
    - Remember Me
    - قفل اکانت پس از ۵ تلاش ناموفق (۱۵ دقیقه)
    - بلاک IP پس از ۳ بار قفل
    - کپچا پس از ۳ تلاش ناموفق
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    # Get failed attempts from session
    failed_attempts = request.session.get('failed_login_attempts', 0)
    show_captcha = failed_attempts >= 3

    # Generate captcha if needed
    if show_captcha and request.method == 'GET':
        question, answer = generate_captcha()
        request.session['captcha_answer'] = answer
    else:
        question = request.session.get('captcha_question', '')

    if request.method == 'POST':
        form = LoginForm(request.POST)

        # Regenerate captcha for display
        if show_captcha:
            question, answer = generate_captcha()
            request.session['captcha_question'] = question

        if form.is_valid():
            student_id = form.cleaned_data['student_id']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)

            # Check captcha if needed
            if show_captcha:
                captcha_input = request.POST.get('captcha', '')
                captcha_answer = request.session.get('captcha_answer', '')
                if captcha_input != captcha_answer:
                    messages.error(request, 'پاسخ کپچا نادرست است.')
                    new_q, new_a = generate_captcha()
                    request.session['captcha_answer'] = new_a
                    return render(request, 'accounts/login.html', {
                        'form': form,
                        'show_captcha': True,
                        'captcha_question': new_q,
                    })

            # Find user
            try:
                user = User.objects.get(student_id=student_id)
            except User.DoesNotExist:
                failed_attempts += 1
                request.session['failed_login_attempts'] = failed_attempts
                messages.error(request, 'شماره شناسایی یا رمز عبور اشتباه است.')
                new_q, new_a = generate_captcha()
                request.session['captcha_answer'] = new_a
                return render(request, 'accounts/login.html', {
                    'form': form,
                    'show_captcha': failed_attempts >= 3,
                    'captcha_question': new_q if failed_attempts >= 3 else '',
                })

            # Check if account is locked
            if user.locked_until and user.locked_until > timezone.now():
                remaining = (user.locked_until - timezone.now()).seconds // 60
                messages.error(
                    request,
                    f'اکانت شما قفل شده است. لطفاً {remaining + 1} دقیقه دیگر تلاش کنید.'
                )
                return render(request, 'accounts/login.html', {
                    'form': form, 'show_captcha': show_captcha,
                    'captcha_question': question,
                })

            # Check IP block
            client_ip = get_client_ip(request)
            ip_locks = request.session.get('ip_lock_count', 0)
            if ip_locks >= settings.MAX_IP_LOCKS:
                messages.error(request, 'آدرس IP شما به دلیل تلاش‌های مکرر ناموفق مسدود شده است.')
                return render(request, 'accounts/login.html', {
                    'form': form, 'show_captcha': True,
                    'captcha_question': question,
                })

            # Check if email is verified
            if not user.is_verified:
                request.session['verification_user_id'] = user.id
                messages.warning(request, 'ایمیل شما هنوز تایید نشده است. لطفاً ابتدا ایمیل خود را تایید کنید.')
                return redirect('accounts:verify_email')

            # Authenticate
            auth_user = authenticate(request, username=student_id, password=password)

            if auth_user is not None:
                # Successful login — reset counters
                user.failed_login_attempts = 0
                user.locked_until = None
                user.save()
                request.session['failed_login_attempts'] = 0
                request.session['ip_lock_count'] = 0

                login(request, auth_user)

                # Remember Me
                if remember_me:
                    request.session.set_expiry(30 * 24 * 3600)  # 30 days
                else:
                    request.session.set_expiry(0)  # Browser close

                messages.success(request, f'خوش آمدید، {auth_user.first_name}!')
                return redirect('accounts:dashboard')
            else:
                # Failed login
                user.failed_login_attempts += 1
                failed_attempts += 1
                request.session['failed_login_attempts'] = failed_attempts

                # Lock account after 5 failed attempts
                if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                    user.locked_until = timezone.now() + timezone.timedelta(
                        seconds=settings.LOGIN_LOCKOUT_DURATION
                    )
                    user.ip_lock_count += 1
                    request.session['ip_lock_count'] = request.session.get('ip_lock_count', 0) + 1
                    user.failed_login_attempts = 0  # Reset for next round
                    user.save()
                    messages.error(request, 'اکانت شما به مدت ۱۵ دقیقه قفل شد.')
                else:
                    user.save()
                    remaining = settings.MAX_LOGIN_ATTEMPTS - user.failed_login_attempts
                    messages.error(
                        request,
                        f'شماره شناسایی یا رمز عبور اشتباه است. {remaining} تلاش باقیمانده.'
                    )

                new_q, new_a = generate_captcha()
                request.session['captcha_answer'] = new_a
                return render(request, 'accounts/login.html', {
                    'form': form,
                    'show_captcha': failed_attempts >= 3,
                    'captcha_question': new_q if failed_attempts >= 3 else '',
                })
    else:
        form = LoginForm()
        if show_captcha:
            question, answer = generate_captcha()
            request.session['captcha_answer'] = answer

    return render(request, 'accounts/login.html', {
        'form': form,
        'show_captcha': show_captcha,
        'captcha_question': question if show_captcha else '',
    })


def logout_view(request):
    """Logout and redirect to login page."""
    logout(request)
    messages.success(request, 'با موفقیت خارج شدید.')
    return redirect('accounts:login')


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
