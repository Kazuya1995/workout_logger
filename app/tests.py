from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Exercise, WorkoutSession, WorkoutSet
import datetime

class WorkoutAppTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='password123')

        # Create a client
        self.client = Client()

        # Create some exercises
        self.predefined_exercise = Exercise.objects.create(name='Bench Press', category='Chest')
        self.custom_exercise = Exercise.objects.create(name='My Custom Exercise', category='Arms', user=self.user)

        # Create a workout session
        self.session = WorkoutSession.objects.create(user=self.user, date=datetime.date.today())

        # Create a workout set
        self.set = WorkoutSet.objects.create(session=self.session, exercise=self.predefined_exercise, reps=10, weight=50)

    def test_model_str_methods(self):
        self.assertEqual(str(self.predefined_exercise), 'Bench Press')
        self.assertEqual(str(self.session), f"testuser's workout on {datetime.date.today()}")
        self.assertEqual(str(self.set), '10 reps of Bench Press at 50.0kg')

    def test_user_registration(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'newpassword123',
            'password2': 'newpassword123',
        })
        user_exists = User.objects.filter(username='newuser').exists()
        self.assertTrue(user_exists)

    def test_login_required_views(self):
        # Test that dashboard redirects to login if not authenticated
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

        # Test that other views also redirect
        response = self.client.get(reverse('add_workout_session'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('add_workout_session')}")

        response = self.client.get(reverse('workout_session_detail', args=[self.session.id]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('workout_session_detail', args=[self.session.id])}")

    def test_dashboard_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{reverse("workout_session_detail", args=[self.session.id])}"')

    def test_add_workout_session(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('add_workout_session'), {
            'date': '2025-01-01'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(WorkoutSession.objects.filter(user=self.user, date='2025-01-01').exists())

    def test_add_workout_set(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('workout_session_detail', args=[self.session.id]), {
            'exercise': self.predefined_exercise.id,
            'reps': 12,
            'weight': 60
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(WorkoutSet.objects.filter(session=self.session, reps=12, weight=60).exists())

    def test_add_custom_exercise(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('add_custom_exercise'), {
            'name': 'Another Custom Exercise',
            'category': 'Legs'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Exercise.objects.filter(user=self.user, name='Another Custom Exercise').exists())

    def test_progress_chart_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('progress_chart'))
        self.assertEqual(response.status_code, 200)

        # Test with an exercise selected
        response = self.client.get(reverse('progress_chart'), {'exercise': self.predefined_exercise.id})
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.context)
        self.assertIn('labels', response.context['data'])
        self.assertEqual(len(response.context['data']['labels']), 1)
        self.assertEqual(response.context['data']['datasets'][0]['data'][0], 50)
