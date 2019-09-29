from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('category/<category>/', views.category, name='category'),
    path('quiz/<title>/', views.show, name='show'),
    path('answer/<int:quiz_order>/', views.answer, name='answer'),
    path('badge/', views.badge, name='badge'),
    path('playground/', views.playground, name='playground'),
    path('manage/', views.manage, name='manage'),
    path('signup/', views.signup, name='signup'),
    path("signin/", views.signin, name="signin"),
    path("signout/", views.signout, name="signout"),
    path("about/", views.about, name="about"),
    path("quiz/<int:quiz_order>/score/<int:score>/", views.quiz_score, name="quiz_score"),
    path("search/", views.search, name="search"),
    path('robots.txt', TemplateView.as_view(template_name="list/robots.txt", content_type='text/plain')),
]
