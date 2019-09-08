from django.urls import path

from . import views

urlpatterns = [
    path('', views.categories, name='categories'),
    path('category/<category>', views.category, name='category'),
    path('<int:quiz_order>/', views.show, name='show'),
    path('answer/<int:quiz_order>/', views.answer, name='answer'),
    path('badge/', views.badge, name='badge'),
    path('playground/', views.playground, name='playground'),
    path('manage/', views.manage, name='manage'),
    path('signup/', views.signup, name='signup'),
    path("signin/", views.signin, name="signin"),
    path("signout/", views.signout, name="signout"),
    path("about/", views.about, name="about"),
    path("quiz/<int:quiz_order>/score/<int:score>", views.quiz_score, name="quiz_score"),
]
