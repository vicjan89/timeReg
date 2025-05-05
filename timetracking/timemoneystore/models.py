from datetime import datetime

from django.db import models

class Task(models.Model):
    name = models.CharField(max_length=100)
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, related_name='child_tasks',
                                    blank=True, null=True, verbose_name='Parent Task')
    planned_time = models.FloatField(default=0, verbose_name='Planned Time', blank=True)
    deadline = models.DateTimeField(blank=True, null=True, verbose_name='Deadline')
    done = models.BooleanField(default=False, verbose_name='Done')
    time_spent = models.FloatField(default=0, verbose_name='Time Spent, hours', blank=True)
    paid = models.FloatField(default=0, verbose_name='Paid', blank=True)

    def __str__(self):
        parent = f'({self.parent_task})' if self.parent_task else ''
        return f'{self.name} {parent}'

class Time(models.Model):
    time_start = models.DateTimeField(verbose_name="Start Time", auto_now_add=False, default=datetime.now)
    time_end = models.DateTimeField(verbose_name="End Time", auto_now_add=False,
                                    default="2025-05-05 12:00:00")
    task = models.ForeignKey(Task, verbose_name="Task", on_delete=models.CASCADE, related_name='time_starts')

    def __str__(self):
        return f'{self.time_start:%Y-%m-%d %H:%M} {self.time_end:%H:%M} {self.task}'

class Payment(models.Model):
    cost = models.PositiveIntegerField(verbose_name="Cost")
    date = models.DateField(verbose_name="Date")
    task = models.ForeignKey(Task, verbose_name="Task", on_delete=models.CASCADE, related_name='payments')

    def __str__(self):
        return f'{self.task} {self.cost} {self.date}'

class Event(models.Model):
    name = models.CharField(max_length=100, verbose_name="Event")
    lower_limit = models.FloatField(verbose_name="Lower Limit", null=True, blank=True)
    upper_limit = models.FloatField(verbose_name="Upper Limit", null=True, blank=True)
    unit = models.CharField(max_length=100, verbose_name="Unit", null=True, blank=True)

    def __str__(self):
        return f'{self.name}'

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, verbose_name="Event", on_delete=models.CASCADE, related_name='parameters')
    value = models.FloatField(verbose_name="Value", null=True, blank=True)
    time_start = models.DateTimeField(verbose_name="start", null=True, blank=True)
    time_end = models.DateTimeField(verbose_name="end", blank=True, null=True)