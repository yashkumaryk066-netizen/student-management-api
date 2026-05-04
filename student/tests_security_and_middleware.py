from django.test import TestCase, Client
from django.contrib.auth.models import User
from student.models import UserProfile, ClientSubscription
from django.utils import timezone
from datetime import date, timedelta
from django.urls import reverse
import json

class MiddlewareAndSecurityTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        # Profile is created by signal
        self.profile = UserProfile.objects.get(user=self.user)
        self.profile.role = 'ADMIN'
        self.profile.institution_type = 'COACHING'
        self.profile.subscription_expiry = date.today() + timedelta(days=30)
        self.profile.save()
        
    def test_security_headers_present(self):
        """Test that OWASP security headers are present in responses"""
        response = self.client.get('/')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'SAMEORIGIN')
        self.assertIn('Content-Security-Policy', response)
        self.assertIn('Permissions-Policy', response)

    def test_subscription_expiry_blocks_api(self):
        """Test that expired subscriptions block API write access"""
        # Expire the plan
        self.profile.subscription_expiry = date.today() - timedelta(days=1)
        self.profile.save()
        
        self.client.force_login(self.user)
        
        # Access a non-exempt URL (e.g., students list)
        # Note: Middleware blocks based on path keywords
        response = self.client.get('/api/students/', HTTP_ACCEPT='application/json')
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['code'], 'SUBSCRIPTION_EXPIRED')

    def test_subscription_exempt_urls(self):
        """Test that auth and payment URLs are NOT blocked even if expired"""
        self.profile.subscription_expiry = date.today() - timedelta(days=1)
        self.profile.save()
        
        self.client.force_login(self.user)
        
        # Auth endpoint should be exempt
        response = self.client.get('/api/auth/profile/')
        self.assertNotEqual(response.status_code, 403)

    def test_feature_gating_restricted(self):
        """Test that features not in plan are blocked (COACHING can't access library)"""
        self.profile.institution_type = 'COACHING'
        self.profile.subscription_expiry = date.today() + timedelta(days=30)
        self.profile.save()
        
        self.client.force_login(self.user)
        
        # /api/library/ is restricted for COACHING
        response = self.client.get('/api/library/', HTTP_ACCEPT='application/json')
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('PLAN_RESTRICTED', response.json()['error']['code'])

    def test_feature_gating_allowed(self):
        """Test that features in plan are allowed (SCHOOL can access transport)"""
        self.profile.institution_type = 'SCHOOL'
        self.profile.subscription_expiry = date.today() + timedelta(days=30)
        self.profile.save()
        
        self.client.force_login(self.user)
        
        # /api/transport/ is allowed for SCHOOL (based on middleware matrix)
        # We use a 404 check here because the endpoint exists but we don't have data, 
        # but 403 would mean it's blocked by middleware.
        response = self.client.get('/api/transport/')
        self.assertNotEqual(response.status_code, 403)

    def test_suspicious_user_agent_blocked(self):
        """Test that suspicious user agents are blocked by RequestValidationMiddleware"""
        response = self.client.get('/', HTTP_USER_AGENT='sqlmap/1.4.11#stable (http://sqlmap.org)')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'Access denied')

    def test_large_payload_blocked(self):
        """Test that excessively large payloads are blocked"""
        large_data = "x" * (11 * 1024 * 1024) # 11MB
        response = self.client.post('/api/auth/login/', data={'data': large_data}, content_type='application/json')
        # Content-Length is what matters
        self.assertEqual(response.status_code, 413)
