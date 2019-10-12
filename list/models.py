import re
from django.db import models

from ckeditor.fields import RichTextField
from adminsortable.models import SortableMixin
from django.utils import timezone

from .enums import Right


class QuizType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return str(self.name)


class Difficulty(models.Model):
    name = models.CharField(max_length=20)
    desc = models.TextField(default=None, blank=True, null=True)
    name_url = ""

    def __str__(self):
        return str(self.name)

    def set_name_url(self):
        self.name_url = self.name.replace(" ", "-")
        return self


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
    name_url = ""

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

    def set_name_url(self):
        self.name_url = self.name.replace(" ", "-")
        return self


# TODO:: solution after answering
class Quiz(SortableMixin):
    default_explanation = """<table border="1" cellpadding="1" cellspacing="1" class="table table-bordered">
    <tbody>
        <tr>
            <td>
                <p><strong>Block</strong></p>
            </td>
        </tr>
    </tbody>
</table>
"""

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
    title = models.CharField(max_length=100, unique=True)
    video = models.CharField(max_length=100, default=None, blank=True, null=True)
    explanation = RichTextField(default=default_explanation, blank=True, null=True)
    question = RichTextField(default=None, blank=True, null=True)
    example = RichTextField(default=default_example, blank=True, null=True)
    hint = RichTextField(default=None, blank=True, null=True)
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
    score = models.IntegerField(default=0)
    title_url = ""

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
               + str(self.order) + "(" + str(self.id) + "). " + title + "  " + str(self.date.strftime("%m-%d %H:%M"))

    def get_title_url(self):
        return self.title.replace(" ", "-")

    def set_title_url(self):
        self.title_url = self.title.replace(" ", "-")
        return self

    def set_pretty_code(self):
        while True:
            START = "<p>#code</p>"
            END = "<p>#end</p>"
            start_index = self.explanation.find(START)
            if start_index == -1:
                break
            end_index = self.explanation.find(END, start_index)

            self.explanation = self.explanation[:start_index] + '<pre><code class="language-py">' + \
                               "<p>\n</p>" + \
                               self.explanation[start_index + len(START): end_index]\
                                   .replace("\r\n", "")\
                                   .replace("</p><p>", "</p>\n<p>") + \
                               "<p>\n</p>" + \
                               "<p>\n</p>" + \
                               "</code></pre>" + self.explanation[end_index + len(END):]

        self.explanation = re.sub("<p>#run-([\d]*)</p>([\s\S]*?)<p>#end</p>",
        r"""<button class="btn btn-sm btn-primary" type="button" data-toggle="collapse" data-target="#run-\1">
    <img class="icon" src="/static/assets/img/icons/theme/media/play.svg" alt="run icon" data-inject-svg /><span>Run</span>
</button>
<div class="collapse" id="run-\1">
    <br/>
    <img class="icon" src="/static/assets/img/icons/theme/devices/display-1.svg" alt="display icon" data-inject-svg /> <span class="text-success"><b>Output:</b></span>
    <div class="pt-3">\2</div>
</div>""", self.explanation)

        while True:
            START = "<p>#code</p>"
            END = "<p>#end</p>"
            start_index = self.example.find(START)
            if start_index == -1:
                break
            end_index = self.example.find(END, start_index)

            self.example = self.example[:start_index] + '<pre><code class="language-py">' + \
                            "<p>\n</p>" + \
                            self.example[start_index + len(START): end_index] \
                               .replace("\r\n", "") \
                               .replace("</p><p>", "</p>\n<p>") + \
                           "<p>\n</p>" + \
                           "<p>\n</p>" + \
                           "</code></pre>" + self.example[end_index + len(END):]

        return self


class Testcase(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    input = models.TextField(default=None, blank=True, null=True)
    expected_output = models.TextField(default=None, blank=True, null=True)
    expected_stdout = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        return str(self.quiz.order) + "(" + str(
            self.quiz.id) + "). " + self.quiz.title + " - " + self.input + " " + self.expected_output


class CustomUser(models.Model):
    name = models.CharField(max_length=30, db_index=True)
    badges = models.ManyToManyField(Badge)
    point = models.IntegerField(default=10)

    def __str__(self):
        return str(self.name)


class Answer(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, blank=True, null=True)
    answer = models.TextField(default=None, blank=True, null=True)
    customuser = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    right = models.IntegerField(default=Right.NOT_TRY.value)
    input = models.TextField(default=None, blank=True, null=True)
    stdout = models.TextField(default=None, blank=True, null=True)
    expected_stdout = models.TextField(default=None, blank=True, null=True)
    output = models.TextField(default=None, blank=True, null=True)
    expected_output = models.TextField(default=None, blank=True, null=True)
    date = models.DateField(default=timezone.now)
    modified_date = models.DateField(default=timezone.now)

    def __str__(self):
        if self.quiz == None:
            return str(self.customuser) + " " + str(self.date)

        return str(self.quiz.order) + "(" + str(self.quiz.id) + "). " + str(self.customuser) + " " + str(
            self.date.strftime("%Y-%m-%d")) + " right:" + str(
            self.right)

    class Meta:
        index_together = [
            ('date', 'right'),
        ]


class QuizScore(models.Model):
    customuser = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = [
            ('customuser', 'quiz',)
        ]

    def __str__(self):
        return str(self.customuser) + " " + str(self.quiz) + " " + str(self.score)


# Daily Check-in(1), Solve Quiz for MultipleCode(2), Answer(3), Code(5)
class PointType(models.Model):
    name = models.CharField(max_length=20)
    point = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)


class UserPoint(models.Model):
    customuser = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField(default=timezone.now)
    pointtype = models.ForeignKey(PointType, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        index_together = [
            ('customuser', 'date', 'pointtype'),
        ]

    def __str__(self):
        return str(self.date.strftime("%m-%d")) + " " + str(self.customuser) + " " + str(self.pointtype)
