from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import WorkoutSession, WorkoutSet, Exercise
from .forms import WorkoutSessionForm, WorkoutSetForm, ExerciseSelectionForm, ExerciseForm
from django.http import JsonResponse

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    sessions = WorkoutSession.objects.filter(user=request.user).order_by('-date')
    return render(request, 'dashboard.html', {'sessions': sessions})

@login_required
def add_workout_session(request):
    if request.method == 'POST':
        form = WorkoutSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.user = request.user
            session.save()
            return redirect('workout_session_detail', session_id=session.id)
    else:
        form = WorkoutSessionForm()
    return render(request, 'workout_session_form.html', {'form': form})

@login_required
def workout_session_detail(request, session_id):
    session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)
    if request.method == 'POST':
        form = WorkoutSetForm(request.POST)
        if form.is_valid():
            set = form.save(commit=False)
            set.session = session
            set.save()
            return redirect('workout_session_detail', session_id=session.id)
    else:
        form = WorkoutSetForm()

    # Filter exercises to include predefined and user-defined exercises
    form.fields['exercise'].queryset = Exercise.objects.filter(user=request.user) | Exercise.objects.filter(user__isnull=True)

    return render(request, 'workout_session_detail.html', {'session': session, 'form': form})

@login_required
def progress_chart(request):
    form = ExerciseSelectionForm()
    # Populate exercise choices for the current user
    form.fields['exercise'].queryset = Exercise.objects.filter(user=request.user) | Exercise.objects.filter(user__isnull=True)

    data = {}
    if 'exercise' in request.GET:
        exercise_id = request.GET.get('exercise')
        exercise = get_object_or_404(Exercise, id=exercise_id)

        # Get all sets for the selected exercise for the current user
        sets = WorkoutSet.objects.filter(
            session__user=request.user,
            exercise=exercise
        ).order_by('session__date')

        # Prepare data for the chart
        dates = [s.session.date.strftime('%Y-%m-%d') for s in sets]
        weights = [s.weight for s in sets]

        data = {
            'labels': dates,
            'datasets': [{
                'label': f'Weight Progress for {exercise.name}',
                'data': weights,
                'fill': False,
                'borderColor': 'rgb(75, 192, 192)',
                'tension': 0.1
            }]
        }

    return render(request, 'progress_chart.html', {'form': form, 'data': data})

@login_required
def add_custom_exercise(request):
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.user = request.user
            exercise.save()
            messages.success(request, f'Exercise "{exercise.name}" created successfully!')
            return redirect('dashboard') # Or wherever you want to redirect
    else:
        form = ExerciseForm()
    return render(request, 'add_custom_exercise.html', {'form': form})
