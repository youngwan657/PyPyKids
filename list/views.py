from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
import datetime
import subprocess
import os

from .models import Quiz, Answer, TestSet

User = "Dayeon"


def list(request):
    quizs = Quiz.objects.order_by('id').filter(visible=1)
    answers = Answer.objects.filter(name="Dayeon")
    right_quizs = answers.filter(right=1).count()
    wrong_quizs = answers.filter(right=-1).count()
    context = {
        'quizs': quizs,
        'total_quiz': quizs.count(),
        'right': right_quizs,
        'wrong': wrong_quizs,
        'right_percent': right_quizs / quizs.count() * 100,
        'wrong_percent': wrong_quizs / quizs.count() * 100,
    }
    return render(request, 'list/list.html', context)


# class Answer(models.Model):
#     quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
#     answer = models.TextField(default=None, blank=True, null=True)
#     date = models.DateTimeField(auto_now_add=True)
#     name = models.CharField(max_length=20)
#     right = models.IntegerField(default=0)
#     case = models.ForeignKey(TestSet, on_delete=models.CASCADE, blank=True, null=True)
#     wrong_result = models.TextField(default=None, blank=True, null=True)

def show(request, quiz_id):
    quiz = Quiz.objects.filter(id=quiz_id)
    next = Quiz.objects.filter(visible=True).filter(id__gt=quiz_id).first()

    # 1: right, -1: wrong, 0: default
    right = request.GET.get('right')
    wrong_testcase, wrong_answer, expected_answer = "", "", ""
    if quiz[0].quiz_type.name == "Code":
        testset = TestSet.objects.filter(quiz__id=quiz_id)
        wrong_testcase = Answer.objects.filter(quiz__id=quiz_id).filter(name=User)
        wrong_answer = wrong_testcase.wrong_answer
        expected_answer = testset.expected_answer

    context = {
        'quiz': quiz[0],
        'answer': answer,
        'right': right,
        'wrong_testcase': wrong_testcase,
        'actual_answer': wrong_answer,
        'expected_answer': expected_answer,
        'next': next,
    }
    return render(request, 'list/show.html', context)


def answer(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    testset = TestSet.objects.filter(quiz__id=quiz_id)
    answer = Answer.objects.filter(quiz__id=quiz_id).filter(name=User)
    answer.answer = request.POST['answer']
    answer.date = datetime.datetime.now()
    if quiz.quiz_type.name == "Code":
        checkAnswer(quiz)
    else:
        # answer
        if answer[0].answer.replace(" ", "").strip() == testset.expected_answer:
            quiz.right = 1
        else:
            quiz.right = -1

    answer[0].save()

    return HttpResponseRedirect('/' + str(quiz.id) + "?right=" + str(quiz.right))


def checkAnswer(quiz):
    testcase = quiz.testcase.split('\n')[0]
    expected_answer = quiz.testcase.split('\n')[1]

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
    f.write("%s" % answer)
    f.close()
"""

    code = header + quiz.answer + footer
    f = open("checking.py", "w+")
    f.write(code)
    f.close()

    actual_answer = "None"
    try:
        subprocess.run(['python', 'checking.py'] + testcase.split(" "), stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, shell=False, check=True)
        if os.path.exists("checking_answer"):
            f = open("checking_answer", "r")
            actual_answer = f.read()
            f.close()
    except subprocess.CalledProcessError as suberror:
        actual_answer = suberror.stdout.decode('utf-8')

    if str(actual_answer) == expected_answer:
        quiz.right = 1
        quiz.wrong_testcase = ""
    else:
        quiz.right = -1
        quiz.wrong_testcase = testcase + "\n" + expected_answer + "\n" + str(actual_answer)
