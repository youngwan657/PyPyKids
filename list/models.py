from django.db import models

from ckeditor.fields import RichTextField
from adminsortable.models import SortableMixin
from django.utils import timezone

from .right import Right

class QuizType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return str(self.name)


class Difficulty(models.Model):
    name = models.CharField(max_length=20)
    desc = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        return str(self.name)


class BadgeType(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return str(self.name)


class Badge(SortableMixin):
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    name = models.CharField(max_length=20)
    type = models.ForeignKey(BadgeType, on_delete=models.CASCADE, default=None, blank=True, null=True)
    value = models.IntegerField(default=0)
    html = models.TextField(default=None, blank=True, null=True)
    desc = models.TextField(default=None, blank=True, null=True)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Badges'

    def __str__(self):
        return str(self.name)


class CustomUser(models.Model):
    name = models.CharField(max_length=30)
    badges = models.ManyToManyField(Badge)

    def __str__(self):
        return str(self.name)


class Category(SortableMixin):
    difficulty = models.ForeignKey(Difficulty, on_delete=models.CASCADE, default=None, blank=True, null=True)
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    name = models.CharField(max_length=20)
    image = models.CharField(max_length=200, default=None, blank=True, null=True)
    desc = models.TextField(default=None, blank=True, null=True)
    visible = models.BooleanField(default=False)
    total_quiz = 0
    solved_quiz = 0
    unsolved_quiz = 0

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Categories'

    def __str__(self):
        if self.difficulty == None:
            return str(self.name)

        visible = "  "
        if self.visible == False:
            visible = "x "
        return visible + self.difficulty.name + "-" + str(self.order) + ". " + str(self.name)


# TODO:: solution after answering
# TODO:: admin filter by category
class Quiz(SortableMixin):
    default_example = """<p>Example 1:</p>
<table border="1" cellpadding="1" cellspacing="1" class="table table-bordered">
	<tbody>
		<tr>
			<td>
			<p><strong>Input</strong>:&nbsp;</p>
			<p><strong>Output</strong>:&nbsp;</p>
			</td>
		</tr>
	</tbody>
</table>
<p>&nbsp;</p>
<p>Example 2:</p>
<table border="1" cellpadding="1" cellspacing="1" class="table table-bordered">
	<tbody>
		<tr>
			<td>
			<p><strong>Input</strong>:&nbsp;</p>
			<p><strong>Output</strong>:&nbsp;</p>
			</td>
		</tr>
	</tbody>
</table>
"""

    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    title = models.CharField(max_length=100, default=None, blank=True, null=True)
    video = models.CharField(max_length=100, default=None, blank=True, null=True)
    explanation = RichTextField(default=None, blank=True, null=True)
    question = RichTextField(default=None, blank=True, null=True)
    example = RichTextField(default=default_example, blank=True, null=True)
    hint = models.TextField(default=None, blank=True, null=True)
    quiz_type = models.ForeignKey(QuizType, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    visible = models.BooleanField(default=True)
    answer_header = models.TextField(default="def solve(num):", blank=True, null=True)
    option1 = models.TextField(default=None, blank=True, null=True)
    option2 = models.TextField(default=None, blank=True, null=True)
    option3 = models.TextField(default=None, blank=True, null=True)
    option4 = models.TextField(default=None, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    right = Right.NOT_TRY.value

    class Meta:
        ordering = ['-order']
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        visible = "  "
        if self.visible == False:
            visible = "x "

        title = ""
        if self.title != None:
            title = self.title
        return visible + str(self.category.difficulty.id) + "[" + self.category.name + "] " \
               + str(self.order) + ". " + title + "  " + str(self.date.strftime("%m-%d %H:%M")) + "(" + str(
            self.id) + ")"


class Testcase(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    test = models.TextField(default=None, blank=True, null=True)
    expected_answer = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        return str(self.quiz.order) + ". " + self.quiz.title + " - " + self.test + " " + self.expected_answer


class Answer(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, blank=True, null=True)
    answer = models.TextField(default=None, blank=True, null=True)
    name = models.CharField(max_length=20)
    right = models.IntegerField(default=Right.NOT_TRY.value)
    testcase = models.TextField(default=None, blank=True, null=True)
    stdout = models.TextField(default=None, blank=True, null=True)
    output = models.TextField(default=None, blank=True, null=True)
    expected_answer = models.TextField(default=None, blank=True, null=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        if self.quiz == None:
            return self.name + " " + str(self.date)

        return str(self.quiz.order) + ". " + self.name + " " + str(self.date.strftime("%Y-%m-%d")) + " right:" + str(
            self.right)
