from django.contrib import admin

from markdownx.admin import MarkdownxModelAdmin
from .models import Quiz, Answer, TestSet, QuizType, Category

admin.site.register(Quiz, MarkdownxModelAdmin)
admin.site.register(Answer)
admin.site.register(TestSet)
admin.site.register(QuizType)
admin.site.register(Category)
