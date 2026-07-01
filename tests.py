from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import SleepEntry


class SleepEntryModelTests(TestCase):
    def test_sleep_quality_for_healthy_sleep(self):
        user = User.objects.create_user(username='tester', password='secret123')
        entry = SleepEntry.objects.create(
            user=user,
            date='2026-07-01',
            bedtime='22:30',
            wake_time='06:30',
            hours_slept=8,
            note='Felt refreshed after a solid night.',
        )

        self.assertEqual(entry.sleep_quality, 'Excellent')


class SleepEntryViewTests(TestCase):
    def test_home_view_accepts_new_sleep_entry(self):
        user = User.objects.create_user(username='viewer', password='secret123')
        self.client.force_login(user)

        response = self.client.post(reverse('home'), {
            'date': '2026-07-02',
            'bedtime': '23:00',
            'wake_time': '07:00',
            'hours_slept': 7,
            'note': 'A calm and steady night.',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(SleepEntry.objects.filter(hours_slept=7).exists())


class SleepSummaryTests(TestCase):
    def test_summary_reports_average_and_recommendation(self):
        user = User.objects.create_user(username='summaryer', password='secret123')
        SleepEntry.objects.create(user=user, date='2026-07-01', bedtime='22:30', wake_time='06:30', hours_slept=8, note='Great')
        SleepEntry.objects.create(user=user, date='2026-07-02', bedtime='23:10', wake_time='06:40', hours_slept=5, note='Low')

        summary = SleepEntry.summarize_entries(SleepEntry.objects.filter(user=user))

        self.assertEqual(summary['average_hours'], 6.5)
        self.assertEqual(summary['best_day']['hours_slept'], 8)
        self.assertIn('sleep schedule', summary['recommendation'].lower())


class ReactDashboardViewTests(TestCase):
    def test_react_dashboard_page_renders(self):
        user = User.objects.create_user(username='reactuser', password='secret123')
        self.client.force_login(user)
        SleepEntry.objects.create(user=user, date='2026-07-03', bedtime='22:45', wake_time='06:45', hours_slept=7, note='Steady night')

        response = self.client.get(reverse('react_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'React Dashboard')
        self.assertContains(response, 'id="react-root"')
