from django.urls import path

from . import views

urlpatterns = [
    path('', views.all_category, name='all_category'),
    path('category/<category>', views.category, name='category'),
    path('<int:quiz_order>/', views.show, name='show'),
    path('answer/<int:quiz_order>/', views.answer, name='answer'),
    path('badge/', views.badge, name='badge'),
    path('playground/', views.playground, name='playground'),
    path('all/', views.show_all_quiz, name='all_quiz'),
    path('signup/', views.signup, name='signup'),
    path("signin/", views.signin, name="signin"),
    path("signout/", views.signout, name="signout"),
    path("about/", views.about, name="about"),
]
