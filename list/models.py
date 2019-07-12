from django.db import models

class Quiz(models.Model):
    question = models.TextField()
    example = models.TextField(default=None, blank=True, null=True)
    question_date = models.DateTimeField()
    hint = models.TextField(default=None, blank=True, null=True)
    answer = models.TextField(default=None, blank=True, null=True)
    answer_date = models.DateTimeField(default=None, blank=True, null=True)
    right = models.IntegerField(default=0)
    wrong_testcase = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        return self.question
