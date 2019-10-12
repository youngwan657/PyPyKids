from django.shortcuts import render

from list.views.common import *


def manage(request, quiz_order):
    quizzes = Quiz.objects.all()

    quiz = Quiz.objects.get(order=quiz_order)
    quiz.set_title_url().set_pretty_code()

    testcases = Testcase.objects.filter(quiz__order=quiz.order)

    answers = Answer.objects.filter(quiz__order=quiz.order)

    context = {
        'current_page': quiz_order,
        'quizzes': quizzes,
        'quiz': quiz.set_pretty_code(),
        'testcases': testcases,
        'answers': answers,
    }

    return render(request, 'list/manage.html', context)



# TODO:: Answer history

# TODO:: like, comment for answer
# TODO:: profile page
# TODO:: search
# TODO:: key / lock
