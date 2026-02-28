from django.conf import settings

# Internationalization Settings
# Defaults can be overridden in main settings.py

CURRENCY_SYMBOL = getattr(settings, 'STUDENT_CURRENCY_SYMBOL', '₹')
CURRENCY_CODE = getattr(settings, 'STUDENT_CURRENCY_CODE', 'USD')
DATE_FORMAT = getattr(settings, 'STUDENT_DATE_FORMAT', '%d-%b-%Y')

# Business Logic Settings
TRIAL_DAYS = getattr(settings, 'STUDENT_TRIAL_DAYS', 7)
DEFAULT_SUBSCRIPTION_DAYS = getattr(settings, 'STUDENT_SUBSCRIPTION_DAYS', 30)
