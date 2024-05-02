from django.urls import path
from chart.views import chart

app_name = 'chart'
urlpatterns = [
    path('', chart, name='chart'),
]
