from django.db import models

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

# Answer, Code
class QuizType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return str(self.name)


# For, If, Function, Class, Integer, String, List, Set, Dictionary
class Category(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return str(self.name)


# TODO:: reorder
class Quiz(models.Model):
    explanation = MarkdownxField()
    question = models.TextField(default=None, blank=True, null=True)
    example = models.TextField(default=None, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    hint = models.TextField(default=None, blank=True, null=True)
    quiz_type = models.ForeignKey(QuizType, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    visible = models.BooleanField(default=True)
    answer_header = models.TextField(default=None, blank=True, null=True)
    option1 = models.TextField(default=None, blank=True, null=True)
    option2 = models.TextField(default=None, blank=True, null=True)
    option3 = models.TextField(default=None, blank=True, null=True)
    option4 = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        return str(self.id) + ". " + self.question

    def formatted_markdown(self):
        return markdownify(self.explanation)

class TestSet(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    test = models.TextField(default=None, blank=True, null=True)
    expected_answer = models.TextField(default=None, blank=True, null=True)


class Answer(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, blank=True, null=True)
    answer = models.TextField(default=None, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=20)
    right = models.IntegerField(default=0)
    testcase = models.TextField(default=None, blank=True, null=True)
    wrong_result = models.TextField(default=None, blank=True, null=True)
    expected_answer = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        return str(self.id) + ". " + self.name
