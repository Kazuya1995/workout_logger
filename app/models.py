from django.db import models
from django.contrib.auth.models import User

class Exercise(models.Model):
    MUSCLE_GROUPS = [
        ('Legs', 'Legs'),
        ('Chest', 'Chest'),
        ('Arms', 'Arms'),
        ('Back', 'Back'),
        ('Shoulders', 'Shoulders'),
        ('Abs', 'Abs'),
        ('Cardio', 'Cardio'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=MUSCLE_GROUPS)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class WorkoutSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username}'s workout on {self.date}"

class WorkoutSet(models.Model):
    session = models.ForeignKey(WorkoutSession, related_name='sets', on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    reps = models.PositiveIntegerField()
    weight = models.FloatField()

    def __str__(self):
        return f"{self.reps} reps of {self.exercise.name} at {self.weight:.1f}kg"
