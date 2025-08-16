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
    category = forms.ChoiceField(choices=Exercise.MUSCLE_GROUPS)

    class Meta:
        model = WorkoutSet
        fields = ['category', 'exercise', 'reps', 'weight']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['exercise'].queryset = Exercise.objects.none()

        if 'category' in self.data:
            try:
                category = self.data.get('category')
                self.fields['exercise'].queryset = Exercise.objects.filter(category=category).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to an empty queryset
        elif self.instance.pk:
            self.fields['exercise'].queryset = self.instance.exercise.category.exercise_set.order_by('name')

class ExerciseSelectionForm(forms.Form):
    exercise = forms.ModelChoiceField(queryset=Exercise.objects.all())

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'category']
