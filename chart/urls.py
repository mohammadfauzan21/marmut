from django.urls import path
from chart.views import chart, detail_lagu

app_name = 'chart'
urlpatterns = [
    path('', chart, name='chart'),
    path('detail_lagu/', detail_lagu, name='detail_lagu'),
]
