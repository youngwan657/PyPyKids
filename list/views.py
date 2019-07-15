from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
import datetime
import subprocess

from .models import Quiz


def list(request):
    quizs = Quiz.objects.order_by('id')
    right_quizs = quizs.filter(right=1).count()
    wrong_quizs = quizs.filter(right=-1).count()
    context = {
        'quizs': quizs,
        'total_quiz': quizs.count(),
        'right': right_quizs,
        'wrong': wrong_quizs,
        'right_percent': right_quizs / quizs.count() * 100,
        'wrong_percent': wrong_quizs / quizs.count() * 100,
    }
    return render(request, 'list/list.html', context)


def show(request, quiz_id):
    quiz = Quiz.objects.filter(id=quiz_id)
    next = Quiz.objects.filter(visible=True).filter(id__gt=quiz_id).first()

    # 1: right, -1: wrong, 0: default
    right = request.GET.get('right')
    wrong_testcase, actual_answer, expected_answer = quiz[0].wrong_testcase.split("\n")

    context = {
        'quiz': quiz[0],
        'right': right,
        'wrong_testcase': wrong_testcase,
        'actual_answer': actual_answer,
        'expected_answer': expected_answer,
        'next': next,
    }
    return render(request, 'list/show.html', context)


def answer(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    quiz.answer = request.POST['answer']
    quiz.answer_date = datetime.datetime.now()
    if quiz.testcase == "":
        # subjective quiz
        if quiz.answer.replace(" ", "").strip() == quiz.correct_answer:
            quiz.right = 1
        else:
            quiz.right = -1
    else:
        # write code
        checkAnswer(quiz)

    quiz.save()

    return HttpResponseRedirect('/' + str(quiz.id) + "?right=" + str(quiz.right))


def checkAnswer(quiz):
    testcase = quiz.testcase.split('\n')[0]
    expected_answer = quiz.testcase.split('\n')[1]

    header = """import sys
"""

    footer = """
def main(argv):
    s = Solution()
    return s.solve(int(argv[0]), int(argv[1]))
    
if __name__ == "__main__":
   sys.exit(main(sys.argv[1:]))
"""
    code = header + quiz.answer + footer
    f = open("/tmp/python3.py", "w+")
    f.write(code)
    f.close()
    actual_answer = subprocess.call("python /tmp/python3.py " + testcase, shell=True)
    if str(actual_answer) == expected_answer:
        quiz.right = 1
        quiz.wrong_testcase = ""
    else:
        quiz.right = -1
        quiz.wrong_testcase = testcase + "\n" + str(actual_answer) + "\n" + expected_answer
