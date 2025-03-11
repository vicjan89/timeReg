from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import matplotlib
import mpld3

def get_html_graph(x, y, name='Grafik'):
    html = '''<div>
  <canvas id="myChart"></canvas>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<script>
  const ctx = document.getElementById('myChart');

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: [''' + ','.join(x) + '''],
      datasets: [{
        label: ''' + f"'{name}'" + ''',
        data: [''' + ','.join(y) + '''],
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          title: {
                            display: true,
                            text: 'Value'
                        }
        }
      }
    }
  });
</script>'''
    return html

def graph(request):
    # Создаем график
    x_values = request.GET.get('x', '')
    y_values = request.GET.get('y', '')
    name = request.GET.get('name', '')
    x_list = [f"'{x}'" for x in x_values.split(',')]
    y_list = y_values.split(',')
    # if len(hours) > 3:
    #     moving_average = [hours[0], (hours[1]+hours[2])/2]
    #     for i in range(2, len(hours) - 1):
    #         moving_average.append((hours[i-2] + hours[i-1] + hours[i] + hours[i+1]) / 4)
    #     moving_average.append((hours[-3] + hours[-2] + hours[-1]) / 3)
    html = get_html_graph(x_list, y_list, name)
    return HttpResponse(html)

