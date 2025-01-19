from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mpld3

def time_graph(request):
    # Создаем график
    dates = request.GET.get('dates', '')
    hours = request.GET.get('hours', '')
    if dates and hours:
        dates = [datetime.strptime(d, '%Y-%m-%d') for d in dates.split(',')]
        hours = [float(h) for h in hours.split(',')]
    fig, ax = plt.subplots()
    fig.set_size_inches(12, 8)
    ax.plot(dates, hours)

    # Преобразуем график в HTML
    html_str = mpld3.fig_to_html(fig)
    return HttpResponse(html_str)

