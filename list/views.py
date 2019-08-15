from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from datetime import datetime, date, timedelta
import subprocess
import os
import json

from django.db.models import Q

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

from .models import Quiz, Answer, Testcase, Category, Difficulty, User, Badge

USERNAME = "Dayeon"
MONTH = 31


def all_category(request):
    difficulties = Difficulty.objects.order_by('id')
    answers = Answer.objects.filter(name=USERNAME)
    right_quizs = answers.filter(right=1).count()
    wrong_quizs = answers.filter(right=-1).count()
    quizs = Quiz.objects.order_by('order').filter(visible=True)
    unsolved_quizs = quizs
    for answer in answers:
        if answer.right == 1:
            unsolved_quizs = unsolved_quizs.filter(~Q(order=answer.quiz.order))

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
    context['total_counts'] = [right_quizs, wrong_quizs, quizs.count() - right_quizs - wrong_quizs]

    # Badge
    context['badges'] = Badge.objects.filter(user__name=USERNAME)

    # Today's Question
    context['today_quiz'] = unsolved_quizs.order_by('?').first()

    for difficulty in difficulties:
        categories = Category.objects.order_by('order').filter(difficulty=difficulty.id, visible=True)
        all_quizs = Quiz.objects;
        answers = Answer.objects.filter(name=USERNAME, right=1)
        for category in categories:
            quizs = all_quizs.filter(category__name=category.name, visible=True)
            category.total_quiz = quizs.count()
            category.unsolved_quiz = quizs.count()
            for quiz in quizs:
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
    quizs = Quiz.objects.filter(category__name=category, visible=True).order_by('order')
    answers = Answer.objects.filter(name=USERNAME)
    right_quizs = 0
    for quiz in quizs:
        answer = answers.filter(quiz__order=quiz.order)
        quiz.right = 0
        if len(answer) > 0:
            quiz.right = answer[0].right
        if quiz.right == 1:
            right_quizs += 1

    if quizs.count() == 0:
        right_percent = 100
    else:
        right_percent = right_quizs / quizs.count() * 100

    context = {
        "category": category,
        "quizs": quizs,

        "total_quiz": quizs.count(),
        "right": right_quizs,
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

    quizs = Quiz.objects.order_by('id').filter(visible=1).count()
    answers = Answer.objects.filter(name=USERNAME, right=1).count()
    if quizs == answers:
        return render(request, 'list/congrats.html')

    return HttpResponseRedirect('/' + str(quiz.order) + "?right_modal=" + str(answer.right))


def check_answer(testcases, answer):
    header = "import sys, ast, os\n"

    footer = """
def main(argv):
    s = Solution()

    if len(argv) == 1:
        return s.solve(ast.literal_eval(argv[0]))
    elif len(argv) == 2:
        return s.solve(ast.literal_eval(argv[0]), ast.literal_eval(argv[1]))
    elif len(argv) == 3:
        return s.solve(ast.literal_eval(argv[0]), ast.literal_eval(argv[1]), ast.literal_eval(argv[2]))

if __name__ == "__main__":
    answer = main(sys.argv[1:])
    if os.path.exists("checking_answer"):
        os.remove("checking_answer")
    f = open("checking_answer", "w+")
    if type(answer) == tuple:
        for line in answer:
            f.write("%s\\n" % line)
    else:
        f.write("%s" % answer)
    f.close()
"""

    code = header + answer.answer + footer
    f = open("checking.py", "w+")
    f.write(code)
    f.close()

    for testcase in testcases:
        output = "None"
        stdout = ""
        try:
            process = subprocess.run(['python', 'checking.py'] + testcase.test.split("\n"), stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, shell=False, check=True)
            stdout = process.stdout.decode("utf-8")
            if os.path.exists("checking_answer"):
                f = open("checking_answer", "r")
                output = f.read().strip()
                f.close()
        except subprocess.CalledProcessError as suberror:
            output = "\n".join(suberror.stdout.decode('utf-8').split("\n")[1:])

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
    if request.method == "POST":
        f = open("checking.py", "w+")
        code = json.loads(request.body.decode('utf-8'))
        f.write(code['answer'])
        f.close()
        try:
            process = subprocess.run(['python', 'checking.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     shell=False, check=True)
            output = process.stdout.decode("utf-8")
        except subprocess.CalledProcessError as suberror:
            output = "\n".join(suberror.stdout.decode('utf-8').split("\n")[1:])

        return JsonResponse({
            'output': output,
        })
    else:
        return render(request, 'list/playground.html')

def submit_playground(request):
    f = open("checking.py", "w+")
    code = request.POST['code']
    f.write(code)
    f.close()
    try:
        process = subprocess.run(['python', 'checking.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 shell=False, check=True)
        output = process.stdout.decode("utf-8")
    except subprocess.CalledProcessError as suberror:
        output = "\n".join(suberror.stdout.decode('utf-8').split("\n")[1:])

    context = {
        'code': code,
        'output': output,
    }

    return render(request, 'list/playground.html', context)

def test(request):
    response = JsonResponse(
        {"name": "hi", "url": "/1"}
    )
    print(json.loads(request.body.decode('utf-8')))
    return response


# TODO:: undo when writing code.
