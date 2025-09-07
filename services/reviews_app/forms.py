from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Review

class ReviewForm(forms.ModelForm):
    text = forms.CharField(
        label=_('Tu reseña'),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('Write about your experience...'),
        }),
        min_length=10,
        help_text=_('Mínimo 10 caracteres'),
    )

    class Meta:
        model = Review
        fields = ['text']
