# TODO:: category master
from django.shortcuts import render

from list.views.common import *


def badge(request):
    context = {
        'username': get_username(request),
        'badges': Badge.objects.all(),
    }
    return render(request, 'list/badge.html', context)
