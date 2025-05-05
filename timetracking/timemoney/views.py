import os
from datetime import datetime

from django.shortcuts import render
from django.http import FileResponse
from django.conf import settings
from django.http import HttpResponse
import pandas as pd

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

def mermaid2html(source: str):
    html = '''<!doctype html>
    <html lang="en">
      <body>
        <pre class="mermaid">
''' + source + '''
        </pre>
        <script type="module">
          import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
        </script>
      </body>
    </html>'''
    return html

def data2mermaid_xychart(x, y, mean, name='Grafik', max_y = 16):
    source = '''---
config:
    xyChart:
        width: 1500
        height: 900
    themeVariables:
        xyChart:
            titleColor: "#ff0000"
---
xychart-beta
    title "''' + name + '''"
    x-axis[''' + x + ''']
    y-axis "Time (in hours)" 0 --> ''' + f'{max_y:.1f}' + '''
    bar[''' + y + ''']
    line[''' + mean + ''']
    '''
    return source

def graph(request):
    # Создаем график
    x_values = request.GET.get('x', '')
    y_values = request.GET.get('y', '')
    name = request.GET.get('name', '')
    x_list = [f'"{x}"' for x in x_values.split(',')]
    y_series = pd.Series(map(float, y_values.split(',')))
    rolling_mean = y_series.rolling(window=5).mean()
    mean_str = '0,' * 4
    mean_str += ','.join([str(num) for num in rolling_mean.dropna()])
    html = mermaid2html(data2mermaid_xychart(x=','.join(x_list), y=y_values,
                                             mean=mean_str,
                                             name=name,
                                             max_y=y_series.max() * 1.1))
    print(html)
    return HttpResponse(html)

def serve_image(request, filename):
    image_path = os.path.join(settings.MEDIA_ROOT, filename)
    return FileResponse(open(image_path, 'rb'))
