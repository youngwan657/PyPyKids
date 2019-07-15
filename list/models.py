from django.db import models


class Quiz(models.Model):
    explanation = models.TextField(default=None, blank=True, null=True)
    question = models.TextField(default=None, blank=True, null=True)
    example = models.TextField(default=None, blank=True, null=True)
    question_date = models.DateTimeField(default=None, blank=True, null=True)
    hint = models.TextField(default=None, blank=True, null=True)
    answer = models.TextField(default=None, blank=True, null=True)
    answer_date = models.DateTimeField(default=None, blank=True, null=True)
    correct_answer = models.TextField(default=None, blank=True, null=True)
    right = models.IntegerField(default=0)
    testcase = models.TextField(default=None, blank=True, null=True)
    wrong_testcase = models.TextField(default=None, blank=True, null=True)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id) + ". " + self.question
