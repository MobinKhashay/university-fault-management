"""FAQ views. US-20, US-23"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import FAQ, FAQVote


def faq_list_view(request):
    """US-23: صفحه FAQ"""
    category = request.GET.get('category', '')
    search = request.GET.get('q', '')
    faqs = FAQ.objects.all()
    if category: faqs = faqs.filter(category=category)
    if search: faqs = faqs.filter(question__icontains=search) | faqs.filter(answer__icontains=search)
    return render(request, 'faq/faq_list.html', {'faqs': faqs, 'current_category': category, 'search': search, 'categories': FAQ.CATEGORY_CHOICES})


@login_required
def faq_vote_view(request, faq_id):
    """Like/dislike a FAQ."""
    if request.method == 'POST':
        faq = get_object_or_404(FAQ, id=faq_id)
        is_like = request.POST.get('vote') == 'like'
        vote, created = FAQVote.objects.get_or_create(faq=faq, user=request.user, defaults={'is_like': is_like})
        if not created:
            if vote.is_like != is_like:
                vote.is_like = is_like
                vote.save()
        faq.likes = FAQVote.objects.filter(faq=faq, is_like=True).count()
        faq.dislikes = FAQVote.objects.filter(faq=faq, is_like=False).count()
        faq.save()
        return JsonResponse({'likes': faq.likes, 'dislikes': faq.dislikes})
    return JsonResponse({'error': 'POST only'})


@login_required
def faq_manage_view(request):
    """US-20: مدیریت FAQ (admin)"""
    if not request.user.is_admin_user:
        return redirect('accounts:dashboard')
    faqs = FAQ.objects.all().order_by('-dislikes', '-created_at')
    return render(request, 'faq/faq_manage.html', {'faqs': faqs})


@login_required
def faq_create_view(request):
    if not request.user.is_admin_user:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        FAQ.objects.create(
            question=request.POST.get('question', ''),
            answer=request.POST.get('answer', ''),
            category=request.POST.get('category', 'general'),
        )
        messages.success(request, 'سوال اضافه شد.')
        return redirect('faq:manage')
    return render(request, 'faq/faq_form.html', {'categories': FAQ.CATEGORY_CHOICES})


@login_required
def faq_delete_view(request, faq_id):
    if not request.user.is_admin_user:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        get_object_or_404(FAQ, id=faq_id).delete()
        messages.success(request, 'سوال حذف شد.')
    return redirect('faq:manage')
