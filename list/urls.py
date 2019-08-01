from django.urls import path

from . import views

urlpatterns = [
    path('', views.all_category, name='all_category'),
    path('category/<category>', views.category, name='category'),
    path('list/', views.list, name='list'),
    path('<int:quiz_id>/', views.show, name='show'),
    path('answer/<int:quiz_id>/', views.answer, name='answer'),
    path('badge/', views.badge, name='badge'),
]
