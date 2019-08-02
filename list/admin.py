from django.contrib import admin

from .models import Quiz, Answer, Testcase, QuizType, Category, Difficulty, User, Badge

from adminsortable.admin import SortableAdmin

admin.site.register(Quiz, SortableAdmin)
admin.site.register(Answer)
admin.site.register(Testcase)
admin.site.register(QuizType)
admin.site.register(Category, SortableAdmin)
admin.site.register(Difficulty)
admin.site.register(User)
admin.site.register(Badge)
