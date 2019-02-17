import random
import string
import datetime

import math

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone
import pagan


def generate_random_key():
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(10))


def generate_profile_picture():
    img = pagan.Avatar(generate_random_key(), pagan.SHA512)
    return img


class Grade(models.Model):

    name = models.CharField(max_length=50)
    points = models.IntegerField(default=0)

    def rank(self):
        aggregate = Grade.objects.filter(points__gt=self.points).aggregate(
            ranking=models.Count('points'))
        return aggregate['ranking'] + 1

    def __str__(self):
        return self.name

class CaseInsensitiveUserManager(UserManager):
    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})

class User(AbstractUser):
    objects = CaseInsensitiveUserManager()
    points = models.IntegerField(default=0)
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True)

    health = models.IntegerField(default=100)
    health_max = models.IntegerField(default=100)

    total_xp = models.IntegerField(default=0)

    def rank(self):
        aggregate = User.objects.filter(points__gt=self.points).aggregate(
            ranking=models.Count('points'))
        return aggregate['ranking'] + 1

    def health_percent(self):
        return math.floor((self.health / self.health_max) * 100)

    def level(self):
        prev_level = 1  
        while self.total_xp > User.total_xp_for_level(prev_level):
            prev_level += 1
        if self.total_xp != User.total_xp_for_level(prev_level):
            prev_level -= 1
        return prev_level

    def xp_toward_next_level(self):
        return self.total_xp - User.total_xp_for_level(self.level())

    def xp_percent(self):
        return math.floor(self.xp_toward_next_level() / User.total_xp_for_level(self.level()+1) * 100)

    @staticmethod
    def xp_for_level(level):
        if level <= 1:
            return 0
        return (level - 1) * 5

    @staticmethod
    def total_xp_for_level(level):
        return level/2 * ((level - 1) * 5)


class Mission(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    location = models.CharField(max_length=50)
    value = models.IntegerField(default=0)
    xp_points = models.IntegerField(default=5)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)

    def is_future(self):
        return self.start_time > timezone.now()

    def is_expired(self):
        return self.end_time < timezone.now()

    def is_completed_by_user(self, user):
        return CompletedMission.objects.filter(mission=self, user=user) > 0

    def __str__(self):
        return self.title


class CompletedMission(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.mission.title + ' by ' + self.user.username


class MissionKey(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    key = models.CharField(max_length=10, unique=True,
                           default=generate_random_key)
    one_use = models.BooleanField(default=False)
    times_used = models.IntegerField(default=0)

    def __str__(self):
        return self.mission.title + ': ' + self.key
