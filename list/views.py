from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from datetime import datetime, date, timedelta
import subprocess
import os

from django.db.models import Q

from .models import Quiz, Answer, TestSet, Category, Difficulty

User = "Dayeon"


def all_category(request):
    difficulties = Difficulty.objects.order_by('id')
    answers = Answer.objects.filter(name=User)
    right_quizs = answers.filter(right=1).count()
    wrong_quizs = answers.filter(right=-1).count()
    quizs = Quiz.objects.order_by('id').filter(visible=1)
    unsolved_quizs = quizs
    for answer in answers:
        if answer.right == 1:
            unsolved_quizs = unsolved_quizs.filter(~Q(id=answer.quiz.id))

    now = date.today() + timedelta(days=+1)
    labels, counts = [], []
    for i in range(0, 30):
        now += timedelta(days=-1)
        if now.strftime("%d") == "01":
            labels.insert(0, now.strftime("%b %d"))
        else:
            labels.insert(0, now.strftime("%d"))
        counts.insert(0, answers.filter(date__date=now).count())

    # For profile
    context = {
        "difficulties": difficulties,
        "quizs": unsolved_quizs,
        "total_quiz": quizs.count(),
        "right": right_quizs,
        "wrong": wrong_quizs,
        "right_percent": right_quizs / quizs.count() * 100,
        "wrong_percent": wrong_quizs / quizs.count() * 100,
        "labels": labels,
        "counts": counts,
    }

    for difficulty in difficulties:
        categories = Category.objects.order_by('order').filter(difficulty=difficulty.id)
        all_quizs = Quiz.objects;
        answers = Answer.objects.filter(name=User, right=1)
        for category in categories:
            quizs = all_quizs.filter(category__name=category.name, visible=True)
            category.total_quiz = quizs.count()
            category.unsolved_quiz = quizs.count()
            for quiz in quizs:
                if len(answers.filter(quiz__id=quiz.id)) == 1:
                    category.unsolved_quiz -= 1

        context["level" + str(difficulty.id)] = categories

    return render(request, 'list/all_category.html', context)


# TODO:: delete
def list(request):
    quizs = Quiz.objects.order_by('id').filter(visible=1)
    answers = Answer.objects.filter(name=User)
    right_quizs = answers.filter(right=1).count()
    wrong_quizs = answers.filter(right=-1).count()

    unsolved_quizs = quizs
    for answer in answers:
        if answer.right == 1:
            unsolved_quizs = unsolved_quizs.filter(~Q(id=answer.quiz.id))

    if len(unsolved_quizs) == 0:
        return render(request, 'list/congrats.html')

    context = {
        'quizs': unsolved_quizs,
        'total_quiz': quizs.count(),
        'right': right_quizs,
        'wrong': wrong_quizs,
        'right_percent': right_quizs / quizs.count() * 100,
        'wrong_percent': wrong_quizs / quizs.count() * 100,
    }
    return render(request, 'list/list.html', context)


def category(request, category):
    quizs = Quiz.objects.filter(category__name=category, visible=True).order_by('id')
    answers = Answer.objects.filter(name=User)
    right_quizs = 0
    for quiz in quizs:
        answer = answers.filter(quiz__id=quiz.id)
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


def show(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    next = Quiz.objects.filter(visible=True).filter(id__gt=quiz_id).first()

    right_modal = request.GET.get('right_modal')
    right, user_answer, testcase, actual_answer, expected_answer = 0, "", "", "", ""
    answer = Answer.objects.filter(quiz__id=quiz_id, name=User)
    if len(answer) == 1:
        right = answer[0].right
        user_answer = answer[0].answer
        testcase = answer[0].testcase
        actual_answer = answer[0].wrong_result
        expected_answer = answer[0].expected_answer
    else:
        user_answer = quiz.answer_header

    context = {
        'quiz': quiz,
        'user_answer': user_answer,
        'right': right,  # accepted(1) or wrong(-1)
        'right_modal': right_modal,  # accepted(1) or wrong(-1)
        'testcase': testcase,
        'actual_answer': actual_answer,
        'expected_answer': expected_answer,
        'next': next,
    }
    return render(request, 'list/show.html', context)


def answer(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    testsets = TestSet.objects.filter(quiz__id=quiz_id)
    answer, created = Answer.objects.get_or_create(quiz__id=quiz_id, name=User)
    answer.quiz = quiz
    answer.answer = request.POST['answer']
    answer.date = datetime.now()
    if quiz.quiz_type.name == "Code":
        checkAnswer(quiz, testsets, answer)
    elif quiz.quiz_type.name == "Answer" or quiz.quiz_type.name == "MultipleChoice":
        # answer
        if answer.answer.replace(" ", "").strip() == testsets[0].expected_answer:
            answer.right = 1
            answer.wrong_result = ""
        else:
            answer.right = -1
            answer.wrong_result = answer.answer

    answer.save()

    quizs = Quiz.objects.order_by('id').filter(visible=1).count()
    answers = Answer.objects.filter(name=User, right=1).count()
    if quizs == answers:
        return render(request, 'list/congrats.html')

    return HttpResponseRedirect('/' + str(quiz.id) + "?right_modal=" + str(answer.right))


def checkAnswer(quiz, testsets, answer):
    header = """import sys, ast, os
"""

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
            print(line)
            f.write("%s\\n" % line)
    else:
        f.write("%s" % answer)
    f.close()
"""

    code = header + answer.answer + footer
    f = open("checking.py", "w+")
    f.write(code)
    f.close()

    for testset in testsets:
        actual_answer = "None"
        try:
            subprocess.run(['python', 'checking.py'] + testset.test.split("\n"), stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, shell=False, check=True)
            if os.path.exists("checking_answer"):
                f = open("checking_answer", "r")
                actual_answer = f.read().strip()
                f.close()
        except subprocess.CalledProcessError as suberror:
            actual_answer = "\n".join(suberror.stdout.decode('utf-8').split("\n")[1:])

        testset.expected_answer = testset.expected_answer.replace("\r\n", "\n")
        if str(actual_answer) != testset.expected_answer.strip():
            answer.right = -1
            answer.testcase = testset.test
            answer.expected_answer = testset.expected_answer
            answer.wrong_result = actual_answer
            return

    answer.right = 1
    answer.testcase = ""
    answer.expected_answer = ""
    answer.wrong_result = ""
