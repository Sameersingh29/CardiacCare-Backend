from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    path('predict/', views.predict, name='predict'),
    path('predict_cardiovascular/',views.predict_cardiovascular, name = 'predict_cardiovascular')
]