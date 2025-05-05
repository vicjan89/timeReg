from django.contrib import admin
from django.urls import path
from . import views

import timetracking.timemoney.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graph/', timetracking.timemoney.views.graph, name='graph'),
    path('media/<str:filename>/', views.serve_image),
]
