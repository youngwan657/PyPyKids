# TODO:: category master
from django.shortcuts import render

from list.views.common import *


def badge(request):
    context = {}
    username = get_username(request)
    context['username'] = username
    context['badges'] = Badge.objects.all()
    context['profile_badge_count'] = get_badge_count(username)
    return render(request, 'list/badge.html', context)
