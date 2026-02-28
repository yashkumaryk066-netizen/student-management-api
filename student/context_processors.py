from .conf import CURRENCY_SYMBOL, CURRENCY_CODE
from django.conf import settings
import time

def global_settings(request):
    """
    Expose global settings to all templates.
    """
    return {
        'CURRENCY_SYMBOL': CURRENCY_SYMBOL,
        'CURRENCY_CODE': CURRENCY_CODE,
        'CACHE_VERSION': getattr(settings, 'STATIC_VERSION', str(int(time.time()))),
    }
