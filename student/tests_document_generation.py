from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from student.models import Student, UserProfile, ClientSubscription
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
import io
import zipfile

class DocumentGenerationTest(APITestCase):
    def setUp(self):
        # Setup Owner
        self.owner = User.objects.create_user(username='owner', password='password123')
        self.profile, _ = UserProfile.objects.get_or_create(user=self.owner)
        self.profile.role = 'CLIENT'
        self.profile.save()
        self.owner.refresh_from_db()
        
        ClientSubscription.objects.create(
            user=self.owner,
            plan_type='INSTITUTE',
            status='ACTIVE',
            end_date=timezone.now().date() + timezone.timedelta(days=30)
        )
        
        # Setup Student
        self.student = Student.objects.create(
            name="PDF Student",
            created_by=self.owner,
            dob="2000-01-01",
            gender="MALE",
            grade=10,
            relation="SELF",
            roll_number="R101"
        )
        
        self.client.force_authenticate(user=self.owner)

    def test_generate_id_card_pdf(self):
        """Test single ID card PDF generation"""
        url = reverse('generate-id-card', kwargs={'student_id': self.student.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(len(response.content) > 0)

    def test_generate_certificate_pdf(self):
        """Test certificate PDF generation"""
        url = reverse('generate-certificate', kwargs={'student_id': self.student.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(len(response.content) > 0)

    def test_bulk_id_cards_zip(self):
        """Test bulk ID cards generation (ZIP containing PDFs)"""
        url = reverse('bulk-id-cards')
        response = self.client.get(url, {'grade': '10'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        
        # Verify ZIP content
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        file_list = zip_file.namelist()
        self.assertTrue(any("IDCard_R101_PDF_Student.pdf" in f for f in file_list))
