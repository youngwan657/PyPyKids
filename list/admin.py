from django.contrib import admin

from .models import Quiz, Answer, TestSet, QuizType, Category, Difficulty

admin.site.register(Quiz)
admin.site.register(Answer)
admin.site.register(TestSet)
admin.site.register(QuizType)
admin.site.register(Category)
admin.site.register(Difficulty)
