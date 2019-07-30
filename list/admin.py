from django.contrib import admin

from .models import Quiz, Answer, TestSet, QuizType, Category, Difficulty

from adminsortable.admin import SortableAdmin

admin.site.register(Quiz)
admin.site.register(Answer)
admin.site.register(TestSet)
admin.site.register(QuizType)
admin.site.register(Category, SortableAdmin)
admin.site.register(Difficulty)
