import subprocess
from datetime import timedelta, date

from django.db.models import Q

from list.models import *

# constants
MONTH = 31


def get_username(request):
    if request.user.is_authenticated:
        return request.user.username
    return ""


def get_unsolved_quizzes(username, quiz_order=-1):
    quizzes = Quiz.objects.filter(visible=True, order__gt=quiz_order).order_by('order')
    if len(quizzes) == 0:
        quizzes = Quiz.objects.filter(visible=True).order_by('order')
    answers = Answer.objects.filter(name=username)
    for answer in answers:
        if answer.right == Right.RIGHT.value:
            quizzes = quizzes.filter(~Q(order=answer.quiz.order))

    return quizzes


# TODO:: move to check when solving quiz.
def add_badge(username):
    if username == "":
        return None

    custom_user = CustomUser.objects.get(name=username)
    answers = Answer.objects.filter(name=username, right=Right.RIGHT.value)
    untaken_badges = Badge.objects.filter(~Q(customuser__name=username))

    # day streak
    now = date.today() + timedelta(days=+1)
    day_streak = 0
    for i in range(0, MONTH):
        now += timedelta(days=-1)
        if answers.filter(date=now, right=Right.RIGHT.value).count() == 0:
            day_streak = i
            break

    for badge in untaken_badges:
        if badge.type.name == "DayStreak" and badge.value <= day_streak:
            custom_user.badges.add(badge)
            custom_user.save()
            return badge

    # quiz per day
    quiz_per_day = answers.filter(date=date.today()).count()
    for badge in untaken_badges:
        if badge.type.name == "QuizPerDay" and badge.value <= quiz_per_day:
            custom_user.badges.add(badge)
            custom_user.save()
            return badge

    # total quiz
    total_quiz = answers.count()
    for badge in untaken_badges:
        if badge.type.name == "TotalQuiz" and badge.value <= total_quiz:
            custom_user.badges.add(badge)
            custom_user.save()
            return badge

    return None


def check_answer(testcases, answer):
    f = open("solution.py", "w+")
    f.write(answer.answer)
    f.close()

    for testcase in testcases:
        output = "None"
        stdout = ""
        try:
            process = subprocess.Popen(['python', 'checking.py'] + testcase.test.split("\n"), stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            outs, errs = process.communicate(timeout=1)
            stdout = outs.decode("utf-8")
            if os.path.exists("checking_answer"):
                f = open("checking_answer", "r")
                output = f.read().strip()
                f.close()
        except subprocess.TimeoutExpired:
            process.kill()
            stdout = "TIMEOUT ERROR"

        testcase.expected_answer = testcase.expected_answer.replace("\r\n", "\n")
        if str(output) != testcase.expected_answer.strip():
            if answer.right == Right.RIGHT.value or answer.right == Right.WRONG_BUT_RIGHT_BEFORE.value:
                answer.right = Right.WRONG_BUT_RIGHT_BEFORE.value
            else:
                answer.right = Right.WRONG.value
            answer.testcase = testcase.test
            answer.expected_answer = testcase.expected_answer
            answer.output = output
            answer.stdout = stdout
            return

    answer.right = Right.RIGHT.value
    answer.testcase = ""
    answer.expected_answer = ""
    answer.output = ""
    answer.stdout = ""
