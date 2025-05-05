import datetime

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from timemoneystore.models import Time, Task, Payment, Event, EventRegistration
import matplotlib.pyplot as plt
plt.switch_backend('Agg')  # Меняет бэкенд на безопасный для серверов
import numpy as np
import pandas as pd


admin.site.site_header = 'timeReg'

def graph(x, y, label_x, label_y, moving_average: bool = False):

    # Создание графика
    plt.figure(figsize=(8, 5))  # Размер графика
    plt.bar(x, y)
    if moving_average:
        # Вычисляем скользящее среднее
        window_size = int(len(x) / 5) + 1  # Размер окна
        y_smooth = pd.Series(y).rolling(window=window_size, center=True).mean()
        plt.plot(x, y_smooth, color="red", linestyle="-",
                 label=f"Moving Average ({window_size=})")

    # Добавление подписей и легенды
    plt.xlabel(label_x)
    # Наклон подписей
    plt.xticks(rotation=45, ha="right")  # ha="right" - выравнивание текста
    plt.ylabel(label_y)
    plt.legend()
    plt.title("Graph of Tasks")
    plt.savefig(settings.MEDIA_ROOT / f'graph.png', dpi=300, bbox_inches="tight")
    plt.close()
    return HttpResponse(f'<img src="/media/graph.png" style="width: auto; height: 100%;" />')


class DateFilter(admin.SimpleListFilter):
    title = 'Date'
    parameter_name = 'date'
    def lookups(self, request, model_admin):
        return [('today', 'Today'),
                ('yesterday', 'Yesterday'),
                ('month', 'Month'),
                ('last_month', 'Last Month'),
                ('penultimate_month', 'Penultimate Month'),
                ('year', 'Year'),
                ('last_year', 'Last Year'),
                ('penultimate_year', 'Penultimate Year'),
                ]

    def queryset(self, request, queryset):
        if self.value() == 'today':
            return queryset.filter(time_start__date=datetime.date.today())
        elif self.value() == 'yesterday':
            return queryset.filter(time_start__date=(datetime.date.today() - datetime.timedelta(days=1)))
        elif self.value() == 'month':
            return queryset.filter(time_start__month=datetime.date.today().month)
        elif self.value() == 'last_month':
            last_month = datetime.date.today().month - 1
            last_month = last_month if last_month > 0 else last_month + 12
            return queryset.filter(time_start__month=last_month)
        elif self.value() == 'penultimate_month':
            month = datetime.date.today().month - 2
            month = month if month > 0 else month + 12
            return queryset.filter(time_start__month=month)
        elif self.value() == 'year':
            return queryset.filter(time_start__year=datetime.date.today().year)
        elif self.value() == 'last_year':
            year = datetime.date.today().year - 1
            return queryset.filter(time_start__year=year)
        elif self.value() == 'penultimate_year':
            year = datetime.date.today().year - 2
            return queryset.filter(time_start__year=year)

@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = ('time_start', 'time_end', 'task')
    actions = ('calc_time', 'calc_time_for_tasks', 'calc_time_for_parents')
    list_filter = [DateFilter]

    def get_form(self, request, obj=None, **kwargs):
        form = super(TimeAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['task'].queryset = Task.objects.filter(done=False)
        return form

    @admin.action(description='Calc time for tasks')
    def calc_time_for_tasks(self, request, queryset):
        tasks = {}
        for time in queryset:
            duration = time.time_end - time.time_start
            if time.task.name != 'Отдых':
                if time.task.name not in tasks:
                    tasks[time.task.name] = duration
                else:
                    tasks[time.task.name] += duration
        durations = []
        task_names = []
        for name, duration in tasks.items():
            task_names.append(name)
            durations.append(duration.total_seconds() / 3600)
        return graph(task_names, durations, "Tasks", "Durations")

    @admin.action(description='Calc time for parents')
    def calc_time_for_parents(self, request, queryset):
        tasks = {}
        for time in queryset:
            duration = time.time_end - time.time_start
            if time.task.name != 'Отдых':
                task = time.task
                name = time.task.name
                while task.parent_task:
                    task = task.parent_task
                    name = task.name
                if name not in tasks:
                    tasks[name] = duration
                else:
                    tasks[name] += duration
        durations = []
        task_names = []
        for name, duration in tasks.items():
            task_names.append(name)
            durations.append(duration.total_seconds() / 3600)
        return graph(task_names, durations, "Tasks", "Durations")


    @admin.action(description='Calc time for day')
    def calc_time(self, request, queryset):
        time_sum = {}
        for time in queryset.reverse():
            if 'Отдых' != time.task.name:
                    date = time.time_start.date()
                    duration = time.time_end - time.time_start
                    if date in time_sum:
                        time_sum[date] += duration
                    else:
                        time_sum[date] = duration
        dates = []
        hours = []
        for date, time in time_sum.items():
            dates.append(date)
            hours.append(time.total_seconds() / 3600)
        return graph(dates, hours, 'Dates', 'Hours', moving_average=True)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_task', 'planned_time', 'deadline', 'done', 'time_spent_formatted', 'paid', 'hour_cost')
    readonly_fields = ('paid', 'hour_cost')
    search_fields = ('name',)
    list_editable = ('done',)
    actions = ('calc_time', 'calc_paid')
    list_filter = ('deadline', 'done')

    def time_spent_formatted(self, obj):
        return f'{obj.time_spent:.2f}'

    def hour_cost(self, obj):
        return f'{obj.paid / obj.time_spent:.1f}' if obj.time_spent else '-'

    @admin.action(description='Calc time spent for task')
    def calc_time(self, request, queryset):
        for task in queryset:
            if task.name != 'Отдых':
                time_sum = datetime.timedelta()
                task_worked = None
                for time in Time.objects.all():
                    if task == time.task or task.child_tasks.contains(time.task):
                        task_worked = time.time_start
                    if task_worked and task != time.task and  not task.child_tasks.contains(time.task):
                        time_sum += time.time_start - task_worked
                        task_worked = None
                if task_worked:
                    try:
                        time_sum += datetime.datetime.now() - task_worked
                    except:
                        ...
                task.time_spent = time_sum.total_seconds() / 3600
                task.save()

    @admin.action(description='Calc for paid task')
    def calc_paid(self, request, queryset):
        for task in queryset:
            if task.name != 'Отдых':
                money = 0.
                for payment in Payment.objects.all():
                    if payment.task == task or task.child_tasks.contains(payment.task):
                        money += payment.cost
                task.paid = money
                task.save()

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('task', 'cost', 'date')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'value', 'time_start', 'time_end')
