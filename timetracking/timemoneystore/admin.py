import datetime

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from timemoneystore.models import Time, Task, Payment, Event, EventRegistration

admin.site.site_header = 'timeReg'

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
    list_display = ('time_start', 'task')
    actions = ('calc_time', 'calc_time_for_task')
    list_filter = [DateFilter]

    def get_form(self, request, obj=None, **kwargs):
        form = super(TimeAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['task'].queryset = Task.objects.filter(done=False)
        return form

    @admin.action(description='Calc time for day')
    def calc_time(self, request, queryset):
        time_sum = {}
        time_worked = None
        for time in queryset.reverse():
            if 'Отдых' != time.task.name:
                time_worked = time
            else:
                if time_worked:
                    date = time_worked.time_start.date()
                    if date in time_sum:
                        time_sum[date] += time.time_start - time_worked.time_start
                    else:
                        time_sum[date] = time.time_start - time_worked.time_start
        dates = []
        hours = []
        for date, time in time_sum.items():
            dates.append(f'{date}')
            hours.append(f'{time.total_seconds() / 3600:.2f}')
        url = reverse('graph')
        return redirect(f'{url}?x=' + ','.join(dates) + '&y=' + ','.join(hours) + '&name=Time for day')

    @admin.action(description='Calc time for task')
    def calc_time_for_task(self, request, queryset):
        time_sum = {}
        time_worked = None
        for time in queryset.reverse():
            if 'Отдых' != time.task.name :
                time_worked = time
            if time_worked and time.task.name != time_worked.task.name:
                if time_worked:
                    task_name = time_worked.task.name
                    if task_name in time_sum:
                        time_sum[task_name] += time.time_start - time_worked.time_start
                    else:
                        time_sum[task_name] = time.time_start - time_worked.time_start
        tasks = []
        hours = []
        for task_name, time in time_sum.items():
            tasks.append(f'{task_name}')
            hours.append(f'{time.total_seconds() / 3600:.2f}')
        url = reverse('graph')
        return redirect(f'{url}?x=' + ','.join(tasks) + '&y=' + ','.join(hours) + '&name=Time for task')


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
