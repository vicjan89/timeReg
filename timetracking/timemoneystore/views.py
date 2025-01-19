from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import mpld3

def time_graph(request):
    # Создаем график
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [1, 4, 9, 16])

    # Преобразуем график в HTML
    html_str = mpld3.fig_to_html(fig)
    return HttpResponse(html_str)

