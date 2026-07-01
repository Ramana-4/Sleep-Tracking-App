from django.contrib.auth.models import User
from django.db import models


class Reminder(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sleep_reminder')
    bedtime = models.TimeField(help_text='Preferred bedtime for reminder')
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.bedtime}"


class SleepEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sleep_entries', null=True, blank=True)
    date = models.DateField()
    bedtime = models.TimeField()
    wake_time = models.TimeField()
    hours_slept = models.PositiveIntegerField()
    note = models.TextField(blank=True)

    @property
    def sleep_quality(self):
        if self.hours_slept >= 8:
            return 'Excellent'
        if self.hours_slept >= 7:
            return 'Good'
        if self.hours_slept >= 6:
            return 'Fair'
        return 'Needs attention'

    @classmethod
    def summarize_entries(cls, queryset):
        entries = list(queryset.order_by('-date'))
        if not entries:
            return {
                'average_hours': 0,
                'best_day': None,
                'recommendation': 'Log a few nights to get a personalized sleep pattern summary.',
            }

        average_hours = round(sum(entry.hours_slept for entry in entries) / len(entries), 1)
        best_day = max(entries, key=lambda entry: entry.hours_slept)
        if average_hours >= 7:
            recommendation = 'Your sleep pattern looks healthy. Keep a steady bedtime and wake-up routine.'
        elif average_hours >= 6:
            recommendation = 'Your sleep is fairly steady. Try to add a little more consistency to your sleep schedule.'
        else:
            recommendation = 'Your sleep pattern needs attention. Aim for a regular bedtime and protect your sleep hours.'

        return {
            'average_hours': average_hours,
            'best_day': {
                'date': best_day.date,
                'hours_slept': best_day.hours_slept,
            },
            'recommendation': recommendation,
        }

    def __str__(self):
        return f"{self.date} - {self.hours_slept}h"
