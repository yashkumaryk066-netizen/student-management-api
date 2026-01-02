from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from student.models import Notification, UserProfile

class NotificationAPITestCase(APITestCase):
    """Test Notification API endpoints"""
    
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_user(username='admin_notif', password='password123')
        UserProfile.objects.create(user=self.admin_user, role='ADMIN')
        
        self.teacher_user = User.objects.create_user(username='teacher_notif', password='password123')
        UserProfile.objects.create(user=self.teacher_user, role='TEACHER')
        
        self.student_user = User.objects.create_user(username='student_notif', password='password123')
        UserProfile.objects.create(user=self.student_user, role='STUDENT')
        
        # Create initial notifications
        self.notif_student = Notification.objects.create(
            recipient_type='STUDENT',
            recipient=self.student_user,
            title='For Student Only',
            message='Hello Student'
        )
        
        self.notif_all = Notification.objects.create(
            recipient_type='ALL',
            title='For Everyone',
            message='Hello All'
        )
        
        self.notif_teacher = Notification.objects.create(
            recipient_type='TEACHER',
            title='For Teachers',
            message='Hello Teachers'
        )

    def test_list_notifications_student(self):
        """Student should see student-specific and ALL notifications"""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        titles = [n['title'] for n in data]
        self.assertIn('For Student Only', titles)
        self.assertIn('For Everyone', titles)
        self.assertNotIn('For Teachers', titles)

    def test_list_notifications_teacher(self):
        """Teacher should see teacher-specific and ALL notifications"""
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        titles = [n['title'] for n in data]
        self.assertIn('For Teachers', titles)
        self.assertIn('For Everyone', titles)
        self.assertNotIn('For Student Only', titles)

    def test_create_notification_admin(self):
        """Admin should be able to create notifications"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'recipient_type': 'STUDENT',
            'title': 'New Event',
            'message': 'Big event upcoming'
        }
        response = self.client.post('/api/notifications/create/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Notification.objects.filter(title='New Event').exists())

    def test_create_notification_student_unauthorized(self):
        """Student should NOT be able to create notifications"""
        self.client.force_authenticate(user=self.student_user)
        data = {
            'recipient_type': 'ALL',
            'title': 'Hacked',
            'message': 'I am hacking'
        }
        response = self.client.post('/api/notifications/create/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_notification_read(self):
        """Identify and mark a notification as read"""
        self.client.force_authenticate(user=self.student_user)
        
        # Ensure it starts unread
        self.assertFalse(self.notif_student.is_read)
        
        url = f'/api/notifications/{self.notif_student.id}/read/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check DB
        self.notif_student.refresh_from_db()
        self.assertTrue(self.notif_student.is_read)
