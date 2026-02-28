from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from student.models import OnlineExam, ExamAttempt, Notification
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Automatically release exam results 5 hours after exam window ends and notify students'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        release_threshold = now - timedelta(hours=5)

        # 1. Find exams that ended 5 hours ago and haven't had results published
        exams_to_release = OnlineExam.objects.filter(
            end_window__lte=release_threshold,
            auto_release_results=True,
            results_published=False
        )

        self.stdout.write(f"Checking for exams to release... Found: {exams_to_release.count()}")

        for exam in exams_to_release:
            self.stdout.write(f"Releasing results for: {exam.title}")
            
            # Mark as published
            exam.results_published = True
            exam.save()

            # 2. Get all students who attempted this exam
            attempts = ExamAttempt.objects.filter(exam=exam, result_notified=False)
            
            for attempt in attempts:
                student = attempt.student
                if not student.email:
                    continue
                
                # Send Email (Portal First Strategy)
                subject = f"IMPORTANT: Result and Certificate Ready for {exam.title}"
                message = f"""
                Hello {student.name},
                
                The results for the examination '{exam.title}' have been officially processed by Sovereign AI.
                
                Your detailed Performance Portfolio, AI Feedback, and Digital Achievement Certificate are now available for viewing and download.
                
                To maintain assessment integrity and view your digital credentials, please log in to your secure portal:
                
                Portal Link: {settings.SITE_URL}/online-exam/
                
                Steps:
                1. Log in with your credentials.
                2. Go to 'Exam History'.
                3. Click on 'View Detailed Result' or 'Download Certificate'.
                
                --
                Regards,
                Y.S.M ERP Automated Proctor System
                """
                
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [student.email],
                        fail_silently=False,
                    )
                    
                    # Create In-App Notification
                    Notification.objects.create(
                        recipient_type='STUDENT',
                        recipient=student.user,
                        title="Exam Result Released",
                        message=f"Result for {exam.title} is now available in your history dashboard."
                    )
                    
                    attempt.result_notified = True
                    attempt.save()
                    self.stdout.write(self.style.SUCCESS(f"Notified {student.name}"))
                    
                except Exception as e:
                    logger.error(f"Failed to send result email to {student.email}: {str(e)}")

        self.stdout.write("Auto-release cycle complete.")
