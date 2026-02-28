
import threading
import logging
from django.core.mail import send_mail
from django.conf import settings
from student.services.invoice_service import generate_invoice_pdf

logger = logging.getLogger(__name__)

class BackgroundThread(threading.Thread):
    """
    Premium Thread Manager for performing non-blocking tasks.
    Used for sending emails, generating PDFs, and heavy calculations.
    """
    def __init__(self, target, args=(), kwargs=None):
        super().__init__()
        self.target = target
        self.args = args
        self.kwargs = kwargs if kwargs else {}
        self._stop_event = threading.Event()

    def run(self):
        try:
            logger.info(f"🚀 Starting Background Task: {self.target.__name__}")
            self.target(*self.args, **self.kwargs)
            logger.info(f"✅ Background Task Completed: {self.target.__name__}")
        except Exception as e:
            logger.error(f"❌ Background Task Failed: {e}", exc_info=True)

def run_in_background(task_func, *args, **kwargs):
    """
    Helper to fire-and-forget a task in a background thread.
    Usage: run_in_background(my_function, arg1, arg2)
    """
    thread = BackgroundThread(target=task_func, args=args, kwargs=kwargs)
    thread.daemon = True # Ensure thread dies if main process dies
    thread.start()

# --- SPECIFIC TASKS ---

def task_send_welcome_email(student_email, student_name, username, password, institution_name, institution_type, payment_id=None):
    """
    Async Task: Generate Invoice PDF and Send Welcome Email
    """
    from student.models import Payment
    
    invoice_pdf = None
    if payment_id:
        try:
            payment = Payment.objects.get(id=payment_id)
            buffer = generate_invoice_pdf(payment)
            invoice_pdf = buffer.getvalue()
        except Exception as e:
            logger.error(f"Failed to generate invoice for student {student_name}: {e}")

    # Construct the email logic locally to avoid circular dependencies with email_service if complex
    # But reusing existing service is better.
    from student.services.email_service import send_student_welcome_email
    
    # Note: We need to pass the raw bytes for PDF if the service supports it, 
    # or handle it here. Assuming service takes raw attributes.
    
    send_student_welcome_email(
        email=student_email,
        student_name=student_name,
        username=username,
        password=password,
        institution_name=institution_name,
        institution_type=institution_type,
        invoice_pdf_bytes=invoice_pdf # Modified service call signature to accept bytes
    )

def task_send_parent_email(parent_email, parent_name, student_name, username, password, institution_name, institution_type):
    from student.services.email_service import send_parent_welcome_email
    send_parent_welcome_email(
        email=parent_email,
        parent_name=parent_name,
        student_name=student_name,
        username=username,
        password=password,
        institution_name=institution_name,
        institution_type=institution_type
    )
