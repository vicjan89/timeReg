import datetime

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from timemoneystore.models import Time, Task, Payment

admin.site.site_header = 'timeReg'

@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = ('time_start', 'task')
    actions = ('calc_time',)

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
        url = reverse('time_graph')
        return redirect(f'{url}?dates=' + ','.join(dates) + '&hours=' + ','.join(hours))

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
