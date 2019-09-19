from django.shortcuts import render
from list.views.common import *


def about(request):
    user = CustomUser.objects.count()
    quiz = Quiz.objects.count()
    video = 0
    for quiz in Quiz.objects.all():
        if quiz.video != None:
            video += 1

    badge = Badge.objects.count()

    context = {
        'username': get_username(request),
        'user': user,
        'video': video,
        'quiz': quiz,
        'badge': badge,
    }
    return render(request, 'list/about.html', context)
