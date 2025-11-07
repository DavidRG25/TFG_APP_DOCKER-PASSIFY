from django import forms

from .models import AllowedImage


class AllowedImageForm(forms.ModelForm):
    suggested_tags = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'readonly': 'readonly'}),
        required=False,
        label='Tags disponibles',
    )

    class Meta:
        model = AllowedImage
        fields = '__all__'
