from django.contrib import admin
from django.utils.html import format_html
from .models import User, EmailVerification, PasswordResetToken

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'first_name', 'last_name', 'role', 'email', 'is_verified', 'show_id_card']
    list_filter = ['role', 'is_verified']
    search_fields = ['first_name', 'last_name', 'student_id', 'email']

    def show_id_card(self, obj):
        if obj.id_card_image:
            return format_html('<a href="{}" target="_blank">🪪 مشاهده</a>', obj.id_card_image.url)
        return '—'
    show_id_card.short_description = 'کارت شناسایی'

admin.site.register(EmailVerification)
admin.site.register(PasswordResetToken)