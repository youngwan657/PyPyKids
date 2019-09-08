from django.shortcuts import render

from list.views.common import *


def manage(request):
    quizzes = Quiz.objects.all()
    testcases = Testcase.objects.all()
    answers = Answer.objects.all()

    context = {
        'quizzes': quizzes,
        'testcases': testcases,
        'answers': answers,
    }
    return render(request, 'list/manage.html', context)



# TODO:: Answer history

# TODO:: point or score
# TODO:: modified date for answer
# TODO:: checking.py for multiple users
# TODO:: set DB primary key
