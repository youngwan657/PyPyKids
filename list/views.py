from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from datetime import datetime, date, timedelta
import subprocess
import os

from django.db.models import Q

from .models import Quiz, Answer, Testcase, Category, Difficulty, User, Badge

USERNAME = "Dayeon"
MONTH = 31


def all_category(request):
    difficulties = Difficulty.objects.order_by('id')
    answers = Answer.objects.filter(name=USERNAME)
    right_quizzes = answers.filter(right=1).count()
    wrong_quizzes = answers.filter(right=-1).count()
    quizzes = Quiz.objects.order_by('order').filter(visible=True)
    unsolved_quizzes = quizzes
    for answer in answers:
        if answer.right == 1:
            unsolved_quizzes = unsolved_quizzes.filter(~Q(order=answer.quiz.order))

    # Chart
    now = date.today() + timedelta(days=+1)
    labels, counts = [], []
    for i in range(0, MONTH):
        now += timedelta(days=-1)
        if now.strftime("%d") == "01" or i == 30:
            labels.insert(0, now.strftime("%b %d"))
        else:
            labels.insert(0, now.strftime("%d"))
        counts.insert(0, answers.filter(date__date=now, right=1).count())

    context = {}
    context['difficulties'] = difficulties
    context['labels'] = labels
    context['counts'] = counts

    # Circle chart
    context['total_labels'] = ["Accepted", "Wrong", "Not Try"]
    context['total_counts'] = [right_quizzes, wrong_quizzes, quizzes.count() - right_quizzes - wrong_quizzes]

    # Badge
    context['badges'] = Badge.objects.filter(user__name=USERNAME)

    # Today's Question
    context['quiz'] = unsolved_quizzes.order_by('?').first()

    for difficulty in difficulties:
        categories = Category.objects.order_by('order').filter(difficulty=difficulty.id, visible=True)
        all_quizzes = Quiz.objects;
        answers = Answer.objects.filter(name=USERNAME, right=1)
        for category in categories:
            quizzes = all_quizzes.filter(category__name=category.name, visible=True)
            category.total_quiz = quizzes.count()
            category.unsolved_quiz = quizzes.count()
            for quiz in quizzes:
                if len(answers.filter(quiz__order=quiz.order)) == 1:
                    category.unsolved_quiz -= 1

        context["level" + str(difficulty.id)] = categories

    return render(request, 'list/all_category.html', context)


# TODO:: category master
def badge(request):
    context = {
        'badges': Badge.objects.all(),
    }
    return render(request, 'list/badge.html', context)


# TODO:: move to check when solving quiz.
def add_badge():
    user = User.objects.get(name=USERNAME)
    answers = Answer.objects.filter(name=USERNAME, right=1)
    untaken_badges = Badge.objects.filter(~Q(user__name=USERNAME))

    # day streak
    now = date.today() + timedelta(days=+1)
    day_streak = 0
    for i in range(0, MONTH):
        now += timedelta(days=-1)
        if answers.filter(date__date=now, right=1).count() == 0:
            day_streak = i
            break

    for badge in untaken_badges:
        if badge.type.name == "DayStreak" and badge.value <= day_streak:
            user.badges.add(badge)
            user.save()
            return badge

    # quiz per day
    quiz_per_day = answers.filter(date__date=datetime.now()).count()
    for badge in untaken_badges:
        if badge.type.name == "QuizPerDay" and badge.value <= quiz_per_day:
            user.badges.add(badge)
            user.save()
            return badge

    # total quiz
    total_quiz = answers.count()

    for badge in untaken_badges:
        if badge.type.name == "TotalQuiz" and badge.value <= total_quiz:
            user.badges.add(badge)
            user.save()
            return badge

    return None


def category(request, category):
    quizzes = Quiz.objects.filter(category__name=category, visible=True).order_by('order')
    answers = Answer.objects.filter(name=USERNAME)
    right_quizzes = 0
    for quiz in quizzes:
        answer = answers.filter(quiz__order=quiz.order)
        quiz.right = 0
        if len(answer) > 0:
            quiz.right = answer[0].right
        if quiz.right == 1:
            right_quizzes += 1

    if quizzes.count() == 0:
        right_percent = 100
    else:
        right_percent = right_quizzes / quizzes.count() * 100

    context = {
        "category": category,
        "quizzes": quizzes,

        "total_quiz": quizzes.count(),
        "right": right_quizzes,
        "right_percent": right_percent,
    }

    return render(request, 'list/category.html', context)


def show(request, quiz_order):
    quiz = get_object_or_404(Quiz, order=quiz_order)
    next = Quiz.objects.filter(visible=True).filter(order__gt=quiz_order).first()

    # TODO: use get instead of filter
    right_modal = request.GET.get('right_modal')
    right, user_answer, testcase, output, stdout, expected_answer = 0, "", "", "", "", ""
    answer = Answer.objects.filter(quiz__order=quiz_order, name=USERNAME)
    if len(answer) == 1:
        right = answer[0].right
        user_answer = answer[0].answer
        testcase = answer[0].testcase
        output = answer[0].output
        stdout = answer[0].stdout
        expected_answer = answer[0].expected_answer
    else:
        user_answer = quiz.answer_header

    new_badge = add_badge()

    context = {
        'new_badge': new_badge,
        'quiz': quiz,
        'user_answer': user_answer,
        'right': right,  # accepted(1) or wrong(-1)
        'right_modal': right_modal,  # accepted(1) or wrong(-1)
        'testcase': testcase,
        'output': output,
        'stdout': stdout,
        'expected_answer': expected_answer,
        'next': next,
    }
    return render(request, 'list/show.html', context)


# TODO: check the object input
# TODO:: dynamic function name depending on quiz.
def answer(request, quiz_order):
    quiz = get_object_or_404(Quiz, order=quiz_order)
    testcases = Testcase.objects.filter(quiz__order=quiz_order)
    answer, created = Answer.objects.get_or_create(quiz__order=quiz_order, name=USERNAME)
    answer.quiz = quiz
    answer.answer = request.POST['answer']
    if answer.right != 1:
        answer.date = datetime.now()

    if quiz.quiz_type.name == "Code":
        check_answer(testcases, answer)
    elif quiz.quiz_type.name == "Answer" or quiz.quiz_type.name == "MultipleChoice":
        # answer
        if answer.answer.replace(" ", "").strip() == testcases[0].expected_answer:
            answer.right = 1
            answer.output = ""
        else:
            answer.right = -1
            answer.output = answer.answer

    answer.save()

    quizzes = Quiz.objects.order_by('id').filter(visible=1).count()
    answers = Answer.objects.filter(name=USERNAME, right=1).count()
    if quizzes == answers:
        return render(request, 'list/congrats.html')

    return HttpResponseRedirect('/' + str(quiz.order) + "?right_modal=" + str(answer.right))


# TODO:: check Node clas
# TODO:: dynamic file name
def check_answer(testcases, answer):
    f = open("solution.py", "w+")
    f.write(answer.answer)
    f.close()

    for testcase in testcases:
        output = "None"
        stdout = ""
        try:
            process = subprocess.Popen(['python', 'checking.py'] + testcase.test.split("\n"), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            outs, errs = process.communicate(timeout=1)
            stdout = outs.decode("utf-8")
            if os.path.exists("checking_answer"):
                f = open("checking_answer", "r")
                output = f.read().strip()
                f.close()
        except subprocess.TimeoutExpired:
            process.kill()
            stdout = "TIMEOUT ERROR"

        # TODO:: check answer correctly.
        testcase.expected_answer = testcase.expected_answer.replace("\r\n", "\n")
        if str(output) != testcase.expected_answer.strip():
            answer.right = -1
            answer.testcase = testcase.test
            answer.expected_answer = testcase.expected_answer
            answer.output = output
            answer.stdout = stdout
            return

    answer.right = 1
    answer.testcase = ""
    answer.expected_answer = ""
    answer.output = ""
    answer.stdout = ""


def playground(request):
    context = {

    }

    return render(request, 'list/playground.html', context)


def submit_playground(request):
    f = open("checking.py", "w+")
    code = request.POST['code']
    f.write(code)
    f.close()
    try:
        process = subprocess.Popen(['python', 'checking.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        outs, errs = process.communicate(timeout=1)
        stdout = outs.decode("utf-8")
    except subprocess.TimeoutExpired:
        process.kill()
        stdout = "TIMEOUT ERROR"

    context = {
        'code': code,
        'stdout': stdout,
    }

    return render(request, 'list/playground.html', context)

def show_all_quiz(request):
    quizzes = Quiz.objects.all()
    testcases = Testcase.objects.all()
    answers = Answer.objects.all()

    context = {
        'quizzes': quizzes,
        'testcases': testcases,
        'answers': answers,
    }
    return render(request, 'list/all_quiz.html', context)


# TODO:: block risky command such as running shell command
