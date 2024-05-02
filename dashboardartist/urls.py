from django.urls import path
from dashboardartist.views import homepageartist, cekroyaltiartist, listsongartist, detaillaguartist

app_name = 'dashboardartist'
urlpatterns = [
    path('', homepageartist, name='homepageartist'),
    path('cekroyaltiartist', cekroyaltiartist, name='cekroyaltiartist'),
    path('listsongartist', listsongartist, name='listsongartist'),
    path('detaillaguartist', detaillaguartist, name='detaillaguartist'),
]
