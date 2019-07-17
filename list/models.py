from django.db import models


# Answer, MultipleChoice, Code
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
# TODO:: multiple-choice problem
class Quiz(models.Model):
    explanation = models.TextField(default=None, blank=True, null=True)
    question = models.TextField(default=None, blank=True, null=True)
    example = models.TextField(default=None, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    hint = models.TextField(default=None, blank=True, null=True)
    quiz_type = models.ForeignKey(QuizType, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id) + ". " + self.question


class TestSet(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    test = models.TextField(default=None, blank=True, null=True)
    expected_answer = models.TextField(default=None, blank=True, null=True)


class Answer(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    answer = models.TextField(default=None, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=20)
    right = models.IntegerField(default=0)
    case = models.ForeignKey(TestSet, on_delete=models.CASCADE, blank=True, null=True)
    wrong_result = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        return str(self.id) + ". " + self.writer
