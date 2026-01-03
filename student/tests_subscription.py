from django.test import TestCase
from django.contrib.auth.models import User
from student.models import ClientSubscription, UserProfile
from django.utils import timezone
from datetime import timedelta

class SubscriptionSystemTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testclient', email='test@client.com', password='password123')
        self.profile = UserProfile.objects.create(user=self.user, role='ADMIN', institution_type='SCHOOL')
        
        # Create initial subscription
        self.sub = ClientSubscription.objects.create(
            user=self.user,
            plan_type='SCHOOL',
            status='PENDING',
            amount_paid=15000
        )

    def test_activation_logic_30_days(self):
        """Test that activation grants exactly 30 days"""
        self.sub.activate(days=30)
        
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.status, 'ACTIVE')
        self.assertIsNotNone(self.sub.start_date)
        self.assertIsNotNone(self.sub.end_date)
        
        # Check duration
        duration = (self.sub.end_date - self.sub.start_date).days
        self.assertEqual(duration, 30)
        
        # Check UserProfile sync
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.subscription_expiry, self.sub.end_date)

    def test_renewal_logic(self):
        """Test that renewing an active plan extends it"""
        # First activate
        self.sub.activate(days=30)
        initial_end = self.sub.end_date
        
        # Renew again (e.g. user pays early)
        self.sub.activate(days=30)
        self.sub.refresh_from_db()
        
        # Should be initial + 30
        expected_end = initial_end + timedelta(days=30)
        self.assertEqual(self.sub.end_date, expected_end)

    def test_expiry_renewal_logic(self):
        """Test that renewing an expired plan starts fresh from today"""
        # Simulate active but expired in past
        past_date = timezone.now().date() - timedelta(days=10)
        self.sub.status = 'ACTIVE'
        self.sub.end_date = past_date
        self.sub.save()
        
        # Renew
        self.sub.activate(days=30)
        self.sub.refresh_from_db()
        
        # Should be today + 30, not past + 30
        today = timezone.now().date()
        expected = today + timedelta(days=30)
        self.assertEqual(self.sub.end_date, expected)
        self.assertEqual(self.sub.status, 'ACTIVE')

    def test_data_preservation(self):
        """Ensure activating subscription does not delete user data"""
        # This is implicit as the method doesn't touch other tables, 
        # but good to sanity check no errors occur
        self.sub.activate(days=30)
        self.assertTrue(User.objects.filter(id=self.user.id).exists())
        self.assertTrue(UserProfile.objects.filter(id=self.profile.id).exists())
