from django.urls import path

from . import views

urlpatterns = [
    path('', views.all_category, name='all_category'),
    path('category/<category>', views.category, name='category'),
    path('list/', views.list, name='list'),
    path('<int:quiz_order>/', views.show, name='show'),
    path('answer/<int:quiz_order>/', views.answer, name='answer'),
    path('badge/', views.badge, name='badge'),
    path('playground/', views.playground, name='playground'),
    path('playground/run/', views.submit_playground, name='playground')
]
