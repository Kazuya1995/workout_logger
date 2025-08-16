from django.contrib import admin
from .models import Exercise, WorkoutSession, WorkoutSet

admin.site.register(Exercise)
admin.site.register(WorkoutSession)
admin.site.register(WorkoutSet)
