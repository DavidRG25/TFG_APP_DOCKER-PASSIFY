# paasify/forms.py
from django import forms
from .models.SubjectModel import Asignatura

class AsignaturaForm(forms.ModelForm):
    class Meta:
        model = Asignatura
        fields = ['nombre', 'año', 'profesor_asignado']