"""
FAQ models.
Related User Stories: US-19, US-20, US-22, US-23
"""

from django.db import models
from django.conf import settings


class FAQ(models.Model):
    """Frequently Asked Questions managed by admin."""

    CATEGORY_CHOICES = [
        ('general', 'عمومی'),
        ('internet', 'اینترنت'),
        ('dormitory', 'خوابگاه'),
        ('rights', 'حقوق'),
        ('facilities', 'تأسیسات'),
        ('other', 'سایر'),
    ]

    question = models.CharField('سوال', max_length=500)
    answer = models.TextField('جواب')
    category = models.CharField('دسته‌بندی', max_length=20, choices=CATEGORY_CHOICES, default='general')
    likes = models.PositiveIntegerField('لایک', default=0)
    dislikes = models.PositiveIntegerField('دیسلایک', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'سوال متداول'
        verbose_name_plural = 'سوالات متداول'
        ordering = ['-created_at']

    def __str__(self):
        return self.question[:80]


class FAQVote(models.Model):
    """Track user votes (like/dislike) on FAQ items."""

    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_like = models.BooleanField('لایک')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'رای FAQ'
        unique_together = ['faq', 'user']

    def __str__(self):
        vote_type = 'لایک' if self.is_like else 'دیسلایک'
        return f"{vote_type} by {self.user} on FAQ #{self.faq.id}"
