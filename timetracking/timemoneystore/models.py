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
    task = models.ForeignKey(Task, verbose_name="Task", on_delete=models.CASCADE, related_name='time_starts')

    def __str__(self):
        return f'{self.time_start:%Y-%m-%d %H:%M} {self.task}'

class Payment(models.Model):
    cost = models.PositiveIntegerField(verbose_name="Cost")
    date = models.DateField(verbose_name="Date")
    task = models.ForeignKey(Task, verbose_name="Task", on_delete=models.CASCADE, related_name='payments')

    def __str__(self):
        return f'{self.task} {self.cost} {self.date}'