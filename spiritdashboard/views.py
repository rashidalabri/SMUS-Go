from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

from .models import Mission, CompletedMission, MissionKey, User, Grade
from django.utils import timezone
from django.views.generic import ListView
import pagan
from .forms import SignUpForm

from django.core.files.storage import default_storage

from projectspirit.settings import MEDIA_DIR, MEDIA_URL


def index(request):
    return HttpResponse('Hi')


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)

            avatar = pagan.Avatar(username, pagan.SHA512)
            avatar.save(MEDIA_DIR, username)

            user.avatar = username + '.png'
            user.save()

            login(request, user)
            return redirect('spiritdashboard:dashboard')
    else:
        form = SignUpForm()

    context = {'form': form}
    return render(request, 'spiritdashboard/register.html', context=context)


@login_required
def dashboard(request):
    if not default_storage.exists(request.user.username + '.png'):
        avatar = pagan.Avatar(request.user.username, pagan.SHA512)
        avatar.save(MEDIA_DIR, request.user.username)
    context = {
        'missions': Mission.objects.all(),
        'grade': request.user.grade,
    }
    return render(request, 'spiritdashboard/dashboard.html', context=context)


@login_required
def claim_key(request, key=None):

    if key is None and request.method == 'POST' and 'key' in request.POST.keys():
        key = request.POST['key']

    # Validates key string
    if len(key) == 10 and len(MissionKey.objects.filter(key=key)) > 0:
        mission_key = MissionKey.objects.filter(key=key)[0]
        mission = mission_key.mission

        # Checks if mission is not expired or in the future, and that it has not been completed before
        if not mission.is_future() and not mission.is_expired() and not CompletedMission.objects.filter(mission=mission, user=request.user):

            if mission_key.one_use and mission_key.times_used > 0:
                return HttpResponseBadRequest(reason='Key provided has already been used.')

            # Creates CompletedMission object and saves it to database
            completed_mission = CompletedMission(
                mission=mission, user=request.user)
            completed_mission.save()

            # Adds points for the user
            request.user.points += mission.value

            # Adds XP points for the user
            request.user.total_xp += mission.xp_points

            # Adds points for the user's grade (if it exists)
            if request.user.grade is not None:
                request.user.grade.points += mission.value

            request.user.save()
            request.user.grade.save()

            return render(request, 'spiritdashboard/completed.html', context={'mission': mission})
    
    return HttpResponseBadRequest(reason='Invalid key, or you have already completed the mission.')


def completed(request):
    return render(request, 'spiritdashboard/completed.html')


class UserLeaderboard(ListView):
    model = User
    template_name = 'spiritdashboard/leaderboards/user.html'
    queryset = User.objects.order_by('-points')[:10]


class GradeLeaderboard(ListView):
    model = Grade
    template_name = 'spiritdashboard/leaderboards/grade.html'
    queryset = Grade.objects.order_by('-points')[:10]

def privacy_policy(request):
    return render(request, 'spiritdashboard/privacy_policy.html')
