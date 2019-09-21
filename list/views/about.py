from django.shortcuts import render
from list.views.common import *


def about(request):
    user_count = CustomUser.objects.count()
    quiz_count = Quiz.objects.count()
    video_count = 0
    for quiz in Quiz.objects.all():
        if quiz.video != None:
            video_count += 1

    badge_count = Badge.objects.count()

    context = {
        'user': user_count,
        'video': video_count,
        'quiz': quiz_count,
        'badge': badge_count,
    }
    get_profile(request, context)
    return render(request, 'list/about.html', context)
