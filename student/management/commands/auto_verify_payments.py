from django.core.management.base import BaseCommand
from student.models import Payment
from django.conf import settings
import email
import imaplib
import re
from datetime import date
from decimal import Decimal

class Command(BaseCommand):
    help = 'Check bank emails for credit alerts and auto-verify UTRs'

    def handle(self, *args, **options):
        # Email Creds
        EMAIL_USER = settings.EMAIL_HOST_USER
        EMAIL_PASS = settings.EMAIL_HOST_PASSWORD
        IMAP_SERVER = 'imap.gmail.com'
        
        try:
            # Login
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(EMAIL_USER, EMAIL_PASS)
            mail.select('inbox')
            
            # Search for bank emails (Simplify: Search unread or last 24h)
            # Searching for "Credit" in subject
            status, messages = mail.search(None, '(SUBJECT "Credit")')
            
            if status != 'OK':
                self.stdout.write(self.style.WARNING("No emails found."))
                return

            for num in messages[0].split():
                status, msg_data = mail.fetch(num, '(RFC822)')
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                subject = msg['subject']
                body = ""
                
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                else:
                    body = msg.get_payload(decode=True).decode()
                
                # --- Parsing Logic (Canara Bank / Generic) ---
                # Look for patterns like "Credited with Rs. 500.00" and "UTR: XXXXX"
                # This is heuristic.
                
                # 1. Extract Amount
                amount_match = re.search(r'(?:Rs\.?|INR)\s*(\d+(?:,\d+)*(?:\.\d{2})?)', body)
                # 2. Extract UTR / Ref
                utr_match = re.search(r'UTR:?\s*([A-Z0-9]+)', body) or re.search(r'Ref:?\s*([A-Z0-9]+)', body)
                
                if amount_match and utr_match:
                    amount = Decimal(amount_match.group(1).replace(',', ''))
                    utr = utr_match.group(1)
                    
                    self.stdout.write(f"Found Credit: {amount} with UTR {utr}")
                    
                    # Verify in DB
                    try:
                        payment = Payment.objects.get(transaction_id=utr, status='PENDING')
                        if payment.amount == amount:
                            payment.status = 'PAID'
                            payment.paid_date = date.today()
                            payment.save()
                            self.stdout.write(self.style.SUCCESS(f"✅ Auto-Verified Payment {utr}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"Mismatch Amount for {utr}: Paid {amount}, Expected {payment.amount}"))
                    except Payment.DoesNotExist:
                        pass
                        
            mail.close()
            mail.logout()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error checking emails: {e}"))
