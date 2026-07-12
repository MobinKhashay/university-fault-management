"""
Report forms.
Related User Stories: US-06
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import Report, Location, FaultCategory


class ReportForm(forms.ModelForm):
    """
    Fault report submission form.
    US-06: ثبت گزارش خرابی با مکان، دسته‌بندی، توضیحات، آپلود
    """

    class Meta:
        model = Report
        fields = ['location', 'category', 'title', 'description', 'priority']
        widgets = {
            'location': forms.HiddenInput(attrs={'id': 'location-id'}),
            'category': forms.Select(attrs={
                'class': 'form-input',
                'id': 'category-select',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'مثال: خرابی پروژکتور کلاس ۲۰۵',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'توضیحات خرابی را با حداقل ۲۰ کاراکتر وارد کنید...',
                'id': 'description-input',
            }),
            'priority': forms.Select(attrs={
                'class': 'form-input',
                'id': 'priority-select',
            }, choices=[
                ('normal', 'عادی'),
                ('important', 'مهم'),
                ('urgent', 'اضطراری'),
            ]),
        }
        labels = {
            'location': 'مکان',
            'category': 'دسته‌بندی خرابی',
            'title': 'عنوان خرابی',
            'description': 'توضیحات',
            'priority': 'سطح فوریت',
        }

    def clean_description(self):
        """Validate minimum 20 characters for description."""
        desc = self.cleaned_data.get('description', '')
        if desc and len(desc) < 20:
            raise ValidationError('توضیحات باید حداقل ۲۰ کاراکتر باشد.')
        return desc
