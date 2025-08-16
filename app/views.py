import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
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
def dashboard(request, year=None, month=None):
    # Calendar logic
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month

    cal = calendar.HTMLCalendar().formatmonth(year, month).replace(
        '<table', '<table class="table table-bordered"'
    )

    current_month = datetime(year, month, 1)
    prev_month = current_month - relativedelta(months=1)
    next_month = current_month + relativedelta(months=1)

    # Get workout data for the current month
    sessions = WorkoutSession.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month
    ).prefetch_related('sets__exercise')

    # Get a list of days with workouts
    workout_days = sessions.values_list('date__day', flat=True).distinct()

    context = {
        'calendar': cal,
        'workout_days': workout_days,
        'sessions': sessions.order_by('-date'),
        'current_month': current_month,
        'prev_month': prev_month,
        'next_month': next_month,
    }

    return render(request, 'dashboard.html', context)

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

@login_required
def daily_workout_detail(request, year, month, day):
    workout_date = date(year, month, day)
    sessions = WorkoutSession.objects.filter(
        user=request.user,
        date=workout_date
    ).prefetch_related('sets__exercise')

    context = {
        'date': workout_date,
        'sessions': sessions,
    }
    return render(request, 'daily_workout_detail.html', context)

@login_required
def log_or_edit_today_workout(request):
    today = date.today()
    session = WorkoutSession.objects.filter(user=request.user, date=today).first()

    if session:
        return redirect('workout_session_detail', session_id=session.id)
    else:
        return redirect('add_workout_session')

def get_exercises_by_category(request):
    category = request.GET.get('category')
    exercises = Exercise.objects.filter(category=category).order_by('name')
    return JsonResponse(list(exercises.values('id', 'name')), safe=False)
