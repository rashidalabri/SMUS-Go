from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import CompletedMission, Grade, Mission, MissionKey, User


class MissionKeyClaimTests(TestCase):

    USERNAME = 'username'
    PASSWORD = 'password'

    def setUp(self):
        self.grade = Grade(name='grade')
        self.grade.save()
        self.user = User.objects.create_user(
            self.USERNAME, password=self.PASSWORD, grade=self.grade)

    def test_claim_mission_key_unauthenticated(self):
        mission = Mission.objects.create(
            title='test_claim_mission_key_unauthenticated', value=50)
        mission_key = MissionKey.objects.create(mission=mission)
        url = reverse('spiritdashboard:claim_key', args=[mission_key.key])
        response = self.client.get(url, follow=True)

        self.assertRedirects(response, '%s?next=%s' %
                             (reverse('spiritdashboard:login'), url))

    def test_claim_mission_key(self):
        mission = Mission.objects.create(
            title='test_claim_mission_key', value=50, end_time=timezone.now() + timedelta(days=1))
        mission_key = MissionKey.objects.create(mission=mission)

        url = reverse('spiritdashboard:claim_key', args=[mission_key.key])

        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        self.client.get(url, follow=True)
        self.client.logout()

        self.assertEqual(len(CompletedMission.objects.filter(
            mission=mission, user=self.user)), 1)

    def test_claim_future_mission_key(self):
        mission = Mission.objects.create(title='test_claim_future_mission_key', value=50, start_time=timezone.now(
        ) + timedelta(days=1), end_time=timezone.now() + timedelta(days=2))
        mission_key = MissionKey.objects.create(mission=mission)

        url = reverse('spiritdashboard:claim_key', args=[mission_key.key])

        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        self.client.get(url, follow=True)
        self.client.logout()

        self.assertEqual(len(CompletedMission.objects.filter(
            mission=mission, user=self.user)), 0)
        return

    def test_claim_expired_mission_key(self):
        mission = Mission.objects.create(title='test_claim_expired_mission_key', value=50, start_time=timezone.now(
        ) - timedelta(days=2), end_time=timezone.now() - timedelta(days=1))
        mission_key = MissionKey.objects.create(mission=mission)

        url = reverse('spiritdashboard:claim_key', args=[mission_key.key])

        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        self.client.get(url, follow=True)
        self.client.logout()

        self.assertEqual(len(CompletedMission.objects.filter(
            mission=mission, user=self.user)), 0)
        return

    def test_claim_mission_key_twice(self):
        mission = Mission.objects.create(
            title='test_claim_mission_key_twice', value=50, end_time=timezone.now() + timedelta(days=1))
        mission_key = MissionKey.objects.create(mission=mission)

        url = reverse('spiritdashboard:claim_key', args=[mission_key.key])

        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        self.client.get(url, follow=True)
        self.client.get(url, follow=True)
        self.client.logout()

        self.assertEqual(len(CompletedMission.objects.filter(
            mission=mission, user=self.user)), 1)

    def test_gain_points_for_user_when_claiming_key(self):
        mission = Mission.objects.create(
            title='test_gain_points_for_user_when_claiming_key', value=50, end_time=timezone.now() + timedelta(days=1))
        mission_key = MissionKey.objects.create(mission=mission)

        points_before = self.user.points

        url = reverse('spiritdashboard:claim_key', args=[mission_key.key])

        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        self.client.get(url, follow=True)
        self.client.logout()

        self.user.refresh_from_db()

        self.assertEqual(self.user.points - points_before, 50)

    def test_gain_points_for_grade_when_claiming_key(self):
        mission = Mission.objects.create(
            title='test_gain_points_for_grade_when_claiming_key', value=50, end_time=timezone.now() + timedelta(days=1))
        mission_key = MissionKey.objects.create(mission=mission)

        points_before = self.grade.points

        url = reverse('spiritdashboard:claim_key', args=[mission_key.key])

        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        self.client.get(url, follow=True)
        self.client.logout()

        self.grade.refresh_from_db()

        self.assertEqual(self.grade.points - points_before, 50)


class LeaderboardTests(TestCase):

    def test_user_ranking(self):
        user1 = User.objects.create_user(username='user1', points=100)
        user2 = User.objects.create_user(username='user2', points=75)
        user3 = User.objects.create_user(username='user3', points=50)
        user4 = User.objects.create_user(username='user4', points=25)

        self.assertEqual(user1.rank(), 1)
        self.assertEqual(user2.rank(), 2)
        self.assertEqual(user3.rank(), 3)
        self.assertEqual(user4.rank(), 4)

    def test_grade_ranking(self):
        grade1 = Grade(name='grade1', points=100)
        grade2 = Grade(name='grade2', points=75)
        grade3 = Grade(name='grade3', points=50)
        grade4 = Grade(name='grade4', points=25)

        grade1.save()
        grade2.save()
        grade3.save()
        grade4.save()

        self.assertEqual(grade1.rank(), 1)
        self.assertEqual(grade2.rank(), 2)
        self.assertEqual(grade3.rank(), 3)
        self.assertEqual(grade4.rank(), 4)


class ProgressionTests(TestCase):

    USERNAME = 'username'
    PASSWORD = 'password'

    def setUp(self):
        self.grade = Grade(name='grade')
        self.grade.save()
        self.user = User.objects.create_user(
            self.USERNAME, password=self.PASSWORD, grade=self.grade)

    def test_xp_for_level(self):
        self.assertEqual(User.xp_for_level(1), 0)
        self.assertEqual(User.xp_for_level(2), 10)
        self.assertEqual(User.xp_for_level(3), 11)
        self.assertEqual(User.xp_for_level(4), 12)
        self.assertEqual(User.xp_for_level(5), 13)

    def test_total_xp_for_level(self):
        self.assertEqual(User.total_xp_for_level(1), 0)
        self.assertEqual(User.total_xp_for_level(2), 10)
        self.assertEqual(User.total_xp_for_level(3), 21)
        self.assertEqual(User.total_xp_for_level(4), 33)
        self.assertEqual(User.total_xp_for_level(5), 46)

    def test_level_when_xp_is_zero(self):
        self.user.total_xp = 0
        self.user.save()
        self.assertEqual(self.user.level(), 1)

    def test_level_when_xp_is_more_than_zero_and_equal_to_total_xp_needed(self):
        self.user.total_xp = 10
        self.user.save()
        self.assertEqual(self.user.level(), 2)

        self.user.total_xp = 21
        self.user.save()
        self.assertEqual(self.user.level(), 3)

        self.user.total_xp = 33
        self.user.save()
        self.assertEqual(self.user.level(), 4)

        self.user.total_xp = 46
        self.user.save()
        self.assertEqual(self.user.level(), 5)


    def test_level_when_xp_is_more_than_zero_and_not_equal_to_total_xp_needed(self):
        self.user.total_xp = 10 + 2
        self.user.save()
        self.assertEqual(self.user.level(), 2)

        self.user.total_xp = 21 + 2
        self.user.save()
        self.assertEqual(self.user.level(), 3)

        self.user.total_xp = 33 + 2
        self.user.save()
        self.assertEqual(self.user.level(), 4)

        self.user.total_xp = 46 + 2
        self.user.save()
        self.assertEqual(self.user.level(), 5)