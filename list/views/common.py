import subprocess
import os
from datetime import timedelta, date

from django.db.models import Q

from list.models import *

# Constants
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


def add_badge(username):
    if username == "":
        return None

    custom_user = CustomUser.objects.get(name=username)
    answers = Answer.objects.filter(name=username, right=Right.RIGHT.value)
    untaken_badges = Badge.objects.filter(~Q(customuser__name=username))

    new_badges = []

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
            new_badges.append({
                'icon': badge.html,
                'desc': badge.desc,
            })

    # quiz per day
    quiz_per_day = answers.filter(date=date.today()).count()
    for badge in untaken_badges:
        if badge.type.name == "QuizPerDay" and badge.value <= quiz_per_day:
            custom_user.badges.add(badge)
            custom_user.save()
            new_badges.append({
                'icon': badge.html,
                'desc': badge.desc,
            })

    # total quiz
    total_quiz = answers.count()
    for badge in untaken_badges:
        if badge.type.name == "TotalQuiz" and badge.value <= total_quiz:
            custom_user.badges.add(badge)
            custom_user.save()
            new_badges.append({
                'icon': badge.html,
                'desc': badge.desc,
            })

    return new_badges