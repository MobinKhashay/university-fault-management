"""
Profile view - add this to accounts/views.py
US-10: ویرایش پروفایل + تغییر رمز
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def profile_view(request):
    from .profile_forms import ProfileForm, ChangePasswordForm

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            form = ProfileForm(request.POST, request.FILES, instance=request.user)
            pw_form = ChangePasswordForm()
            if form.is_valid():
                form.save()
                messages.success(request, 'پروفایل با موفقیت بروزرسانی شد.')
                return redirect('accounts:profile')
        elif 'change_password' in request.POST:
            form = ProfileForm(instance=request.user)
            pw_form = ChangePasswordForm(request.POST)
            if pw_form.is_valid():
                if not request.user.check_password(pw_form.cleaned_data['old_password']):
                    messages.error(request, 'رمز فعلی نادرست است.')
                elif pw_form.cleaned_data['new_password'] != pw_form.cleaned_data['confirm_password']:
                    messages.error(request, 'رمز جدید مطابقت ندارد.')
                else:
                    request.user.set_password(pw_form.cleaned_data['new_password'])
                    request.user.save()
                    messages.success(request, 'رمز تغییر کرد. دوباره وارد شوید.')
                    return redirect('accounts:login')
    else:
        form = ProfileForm(instance=request.user)
        pw_form = ChangePasswordForm()

    stats = {}
    if request.user.is_reporter:
        from reports.models import Report
        reps = Report.objects.filter(reporter=request.user)
        stats = {'total_reports': reps.count(), 'resolved': reps.filter(status__in=['resolved','closed']).count()}

    return render(request, 'accounts/profile.html', {'form': form, 'pw_form': pw_form, 'stats': stats})
