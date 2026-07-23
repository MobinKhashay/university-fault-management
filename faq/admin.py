from django.contrib import admin
from .models import FAQ, FAQVote

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'likes', 'dislikes']
    list_filter = ['category']

admin.site.register(FAQVote)