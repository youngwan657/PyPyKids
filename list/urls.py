from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:quiz_id>/', views.answer, name='answer'),
]
