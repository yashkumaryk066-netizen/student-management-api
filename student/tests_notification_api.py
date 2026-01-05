from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from student.models import Notification, UserProfile


class NotificationAPITestCase(APITestCase):
    """Enterprise-level tests for Notification APIs"""

    def setUp(self):
        # ===== Admin =====
        self.admin_user = User.objects.create_user(
            username='admin_notif',
            password='password123',
            is_staff=True,
            is_superuser=True
        )
        UserProfile.objects.create(user=self.admin_user, role='ADMIN')

        # ===== Teacher =====
        self.teacher_user = User.objects.create_user(
            username='teacher_notif',
            password='password123'
        )
        UserProfile.objects.create(user=self.teacher_user, role='TEACHER')

        # ===== Student =====
        self.student_user = User.objects.create_user(
            username='student_notif',
            password='password123'
        )
        UserProfile.objects.create(user=self.student_user, role='STUDENT')

        # ===== Notifications =====
        self.notif_student = Notification.objects.create(
            recipient_type='STUDENT',
            recipient=self.student_user,
            title='For Student Only',
            message='Hello Student',
            is_read=False
        )

        self.notif_all = Notification.objects.create(
            recipient_type='ALL',
            title='For Everyone',
            message='Hello All',
            is_read=False
        )

        self.notif_teacher = Notification.objects.create(
            recipient_type='TEACHER',
            title='For Teachers',
            message='Hello Teachers',
            is_read=False
        )

    # =========================
    # LIST TESTS
    # =========================
    def test_list_notifications_student(self):
        """Student sees STUDENT + ALL notifications only"""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data if isinstance(response.data, list) else response.data.get('results', [])
        titles = [n['title'] for n in data]

        self.assertIn('For Student Only', titles)
        self.assertIn('For Everyone', titles)
        self.assertNotIn('For Teachers', titles)

    def test_list_notifications_teacher(self):
        """Teacher sees TEACHER + ALL notifications only"""
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data if isinstance(response.data, list) else response.data.get('results', [])
        titles = [n['title'] for n in data]

        self.assertIn('For Teachers', titles)
        self.assertIn('For Everyone', titles)
        self.assertNotIn('For Student Only', titles)

    # =========================
    # CREATE TESTS
    # =========================
    def test_create_notification_admin(self):
        """Admin can create notifications"""
        self.client.force_authenticate(user=self.admin_user)

        payload = {
            'recipient_type': 'STUDENT',
            'title': 'New Event',
            'message': 'Big event upcoming'
        }

        response = self.client.post(
            '/api/notifications/create/',
            payload,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Notification.objects.filter(title='New Event').exists())

    def test_create_notification_student_forbidden(self):
        """Student cannot create notifications"""
        self.client.force_authenticate(user=self.student_user)

        payload = {
            'recipient_type': 'ALL',
            'title': 'Hacked',
            'message': 'I am hacking'
        }

        response = self.client.post(
            '/api/notifications/create/',
            payload,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # =========================
    # READ TESTS
    # =========================
    def test_mark_notification_read(self):
        """Student can mark own notification as read"""
        self.client.force_authenticate(user=self.student_user)

        self.assertFalse(self.notif_student.is_read)

        url = f'/api/notifications/{self.notif_student.id}/read/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.notif_student.refresh_from_db()
        self.assertTrue(self.notif_student.is_read)

    def test_mark_notification_read_twice(self):
        """Marking already-read notification should be safe"""
        self.client.force_authenticate(user=self.student_user)

        url = f'/api/notifications/{self.notif_student.id}/read/'
        self.client.post(url)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_mark_others_notification(self):
        """Student cannot mark teacher notification"""
        self.client.force_authenticate(user=self.student_user)

        url = f'/api/notifications/{self.notif_teacher.id}/read/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
