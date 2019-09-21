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

    username = get_username(request)
    context = {
        'username': username,
        'user': user,
        'video': video,
        'quiz': quiz,
        'badge': badge,
        'profile_badge_count': get_badge_count(username)
    }
    return render(request, 'list/about.html', context)
