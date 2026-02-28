"""
Database Performance Optimization Script
Adds missing indexes to improve query performance
SAFE: Only adds indexes, doesn't modify data or logic
"""

from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Add performance indexes to database (safe operation)'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        
        indexes = [
            # Student table indexes
            "CREATE INDEX IF NOT EXISTS idx_student_email ON student_student(email);",
            "CREATE INDEX IF NOT EXISTS idx_student_roll ON student_student(roll_number);",
            "CREATE INDEX IF NOT EXISTS idx_student_batch ON student_student(batch_id);",
            "CREATE INDEX IF NOT EXISTS idx_student_class ON student_student(class_name);",
            
            # Attendance indexes
            "CREATE INDEX IF NOT EXISTS idx_attendance_date ON student_attendance(date);",
            "CREATE INDEX IF NOT EXISTS idx_attendance_student ON student_attendance(student_id);",
            "CREATE INDEX IF NOT EXISTS idx_attendance_status ON student_attendance(status);",
            
            # Payment indexes
            "CREATE INDEX IF NOT EXISTS idx_payment_status ON student_payment(status);",
            "CREATE INDEX IF NOT EXISTS idx_payment_date ON student_payment(payment_date);",
            "CREATE INDEX IF NOT EXISTS idx_payment_user ON student_payment(user_id);",
            
            # Subscription indexes  
            "CREATE INDEX IF NOT EXISTS idx_subscription_status ON student_clientsubscription(status);",
            "CREATE INDEX IF NOT EXISTS idx_subscription_end ON student_clientsubscription(end_date);",
            
            # Login attempt indexes
            "CREATE INDEX IF NOT EXISTS idx_login_created ON student_loginattempt(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_login_status ON student_loginattempt(status);",
            
            # Library indexes
            "CREATE INDEX IF NOT EXISTS idx_book_isbn ON student_librarybook(isbn);",
            "CREATE INDEX IF NOT EXISTS idx_book_status ON student_librarybook(status);",
            "CREATE INDEX IF NOT EXISTS idx_issue_return ON student_bookissue(return_date);",
        ]
        
        self.stdout.write("Adding performance indexes...")
        
        for idx, sql in enumerate(indexes, 1):
            try:
                cursor.execute(sql)
                self.stdout.write(self.style.SUCCESS(f'  ✓ Index {idx}/{len(indexes)} created'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠ Index {idx} skipped: {str(e)[:50]}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Database optimization complete!'))
        self.stdout.write('   Performance should be noticeably faster.\n')
