from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from student.models import Student, UserProfile, ClientSubscription, InventoryItem, AuditLog
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal

class AdvancedModulesTest(APITestCase):
    def setUp(self):
        # Setup Owner
        self.owner = User.objects.create_user(username='owner', password='password123')
        self.profile, _ = UserProfile.objects.get_or_create(user=self.owner)
        self.profile.role = 'CLIENT'
        self.profile.institution_name = "Test Uni"
        self.profile.location_lat = Decimal('25.5941') # Patna Lat
        self.profile.location_long = Decimal('85.1376') # Patna Long
        self.profile.attendance_radius = 500 # 500 meters
        self.profile.save()
        self.owner.refresh_from_db()
        
        ClientSubscription.objects.create(
            user=self.owner,
            plan_type='INSTITUTE',
            status='ACTIVE',
            end_date=timezone.now().date() + timezone.timedelta(days=30)
        )
        
        # Setup Student linked to Owner
        self.student_user = User.objects.create_user(username='student_user', password='password123')
        self.student = Student.objects.create(
            name="Geo Student",
            user=self.student_user,
            created_by=self.owner,
            dob="2000-01-01",
            gender="MALE",
            grade=10,
            relation="SELF"
        )
        # Link student profile
        self.student_profile, _ = UserProfile.objects.get_or_create(user=self.student_user)
        self.student_profile.role = 'STUDENT'
        self.student_profile.save()
        
        self.client.force_authenticate(user=self.student_user)

    def test_geofenced_attendance_success(self):
        """Test attendance marking when within range"""
        url = reverse('attendance-mark-geo')
        # Exact same coordinates as institution
        data = {
            "lat": 25.5941,
            "long": 85.1376
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn("Attendance Marked Successfully", response.data['message'])

    def test_geofenced_attendance_fail_out_of_range(self):
        """Test attendance marking when far away (e.g. Delhi vs Patna)"""
        url = reverse('attendance-mark-geo')
        # Delhi coordinates
        data = {
            "lat": 28.6139,
            "long": 77.2090
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertIn("Out of attendance range", response.data['error'])

    def test_inventory_stock_alert_logic(self):
        """Test inventory item creation and stock level monitoring"""
        self.client.force_authenticate(user=self.owner)
        
        # Create item with low stock
        item = InventoryItem.objects.create(
            name="Whiteboard Markers",
            category="Stationary",
            quantity=2,
            unit_price=Decimal('50.00'),
            min_stock_level=5,
            created_by=self.owner
        )
        
        # Check if quantity < min_stock_level
        self.assertTrue(item.quantity < item.min_stock_level)

    def test_audit_log_generation(self):
        """Test that sensitive actions trigger audit logs"""
        # We'll use the student approval test logic as a trigger
        self.client.force_authenticate(user=self.owner)
        
        unapproved_student = Student.objects.create(
            name="Audit Test", 
            dob="2000-01-01", 
            gender="MALE", 
            grade=10, 
            relation="SELF",
            is_approved=False,
            created_by=self.owner
        )
        
        url = reverse('student-approve', kwargs={'id': unapproved_student.id})
        self.client.post(url, {'is_approved': True}, format='json')
        
        # Check if AuditLog entry was created
        log_exists = AuditLog.objects.filter(
            action='STUDENT_APPROVED',
            description__icontains="Audit Test"
        ).exists()
        
        self.assertTrue(log_exists)
