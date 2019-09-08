from datetime import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from list.views.common import *


def show(request, quiz_order):
    context = {}
    username = get_username(request)
    context['username'] = username

    answers = Answer.objects.filter(name=username)

    quiz = get_object_or_404(Quiz, order=quiz_order)
    # TODO:: 404 when visible is False

    right_modal = request.GET.get('right_modal')
    answer = answers.filter(quiz__order=quiz_order).first()

    # default answer header
    context['user_answer'] = quiz.answer_header
    if answer:
        context['user_answer'] = answer.answer
        context['answer'] = answer

    context['next'] = get_unsolved_quizzes(username, quiz_order).first()
    context['difficulty'] = quiz.category.difficulty
    context['category'] = quiz.category.name
    context['new_badge'] = add_badge(username)
    context['quiz'] = quiz
    context['right_modal'] = right_modal
    context['quiz_name'] = quiz_order
    # TODO:: change to configurable image for quiz
    context['quiz_image'] = 'theme/devices/airpods.svg'

    context['clicked'] = QuizScore.objects.filter(custom_user_id=request.user.id, quiz_id=quiz.id).exists()

    return render(request, 'list/show.html', context)


# TODO:: check the object input
# TODO:: dynamic function name depending on quiz.
def answer(request, quiz_order):
    quiz = get_object_or_404(Quiz, order=quiz_order)
    testcases = Testcase.objects.filter(quiz__order=quiz_order)
    answer, _ = Answer.objects.get_or_create(quiz_id=quiz.id, name=get_username(request))
    answer.quiz = quiz
    answer.answer = request.POST['answer']
    if answer.right != Right.RIGHT.value and answer.right != Right.WRONG_BUT_RIGHT_BEFORE.value:
        answer.date = datetime.now()

    if quiz.quiz_type.name == "Code":
        check_answer(testcases, answer)
    elif quiz.quiz_type.name == "Answer" or quiz.quiz_type.name == "MultipleChoice":
        # answer
        if answer.answer.replace(" ", "").strip() == testcases[0].expected_answer:
            answer.right = Right.RIGHT.value
            answer.output = ""
        else:
            if answer.right == Right.RIGHT.value or answer.right == Right.WRONG_BUT_RIGHT_BEFORE.value:
                answer.right = Right.WRONG_BUT_RIGHT_BEFORE.value
            else:
                answer.right = Right.WRONG.value
            answer.output = answer.answer

    answer.save()

    return HttpResponseRedirect('/' + str(quiz.order) + "?right_modal=" + str(answer.right))


def quiz_score(request, quiz_order, score):
    quiz = get_object_or_404(Quiz, order=quiz_order)


    quiz_score, _ = QuizScore.objects.get_or_create(custom_user_id=request.user.id, quiz_id=quiz.id)
    quiz.score += score - quiz_score.score
    quiz.save()

    quiz_score.custom_user_id = request.user.id
    quiz_score.quiz = quiz
    quiz_score.score = score
    quiz_score.save()

    return HttpResponseRedirect('/' + str(quiz.order))
