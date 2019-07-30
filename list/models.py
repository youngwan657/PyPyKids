from django.db import models

from django.utils.timezone import now
from ckeditor.fields import RichTextField
from adminsortable.models import SortableMixin


class QuizType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return str(self.name)


class Difficulty(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return str(self.name)


class Category(SortableMixin):
    difficulty = models.ForeignKey(Difficulty, on_delete=models.CASCADE, default=None, blank=True, null=True)
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    name = models.CharField(max_length=20)
    image = models.CharField(max_length=200, default=None, blank=True, null=True)
    desc = models.TextField(default=None, blank=True, null=True)
    total_quiz = 0
    unsolved_quiz = 0

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Categories'

    def __str__(self):
        if self.difficulty == None:
            return str(self.name)

        return self.difficulty.name + "-" + str(self.order) + ". " + str(self.name)


# TODO:: reorder, admin filter
class Quiz(models.Model):
    explanation = RichTextField(default=None, blank=True, null=True)
    video = models.TextField(default=None, blank=True, null=True)
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
    date = models.DateTimeField(default=now)
    right = 0

    def __str__(self):
        visible = "  "
        if self.visible == False:
            visible = "x "
        return visible + str(self.id) + ". " + self.question


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
