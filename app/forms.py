from django import forms
from .models import WorkoutSession, WorkoutSet, Exercise

class WorkoutSessionForm(forms.ModelForm):
    class Meta:
        model = WorkoutSession
        fields = ['date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

class WorkoutSetForm(forms.ModelForm):
    class Meta:
        model = WorkoutSet
        fields = ['exercise', 'reps', 'weight']

class ExerciseSelectionForm(forms.Form):
    exercise = forms.ModelChoiceField(queryset=Exercise.objects.all())

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'category']
