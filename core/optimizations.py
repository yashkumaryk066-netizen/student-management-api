"""
ENTERPRISE-LEVEL BACKEND OPTIMIZATIONS
Django performance utilities and decorators
"""

from functools import wraps
from django.core.cache import cache
from django.db.models import Prefetch, F, Q, Count, Sum
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
import time
import logging

logger = logging.getLogger(__name__)


# ==================== CACHING DECORATORS ====================

def cache_api_response(timeout=300, key_prefix='api'):
    """
    Decorator to cache API responses
    Usage: @cache_api_response(timeout=600)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and args
            cache_key = f"{key_prefix}_{func.__name__}_{str(args)}_{str(kwargs)}"
            
            # Try to get from cache
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                logger.info(f"Cache HIT: {cache_key}")
                return Response(cached_data)
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache the data, not the response object (to avoid rendering/pickling issues)
            if hasattr(result, 'data'):
                cache.set(cache_key, result.data, timeout)
                logger.info(f"Cache MISS: {cache_key} - Cached for {timeout}s")
            
            return result
        return wrapper
    return decorator


def invalidate_cache(key_pattern):
    """
    Helper to invalidate cache on data mutation
    Usage: invalidate_cache('api_students_*')
    """
    # Simple pattern matching for cache clearing
    from django.core.cache import cache
    try:
        cache.delete_pattern(key_pattern)
    except AttributeError:
        # Fallback for LocMemCache (tests) which doesn't support delete_pattern
        cache.clear()


# ==================== QUERY OPTIMIZATION ====================

class OptimizedQueryMixin:
    """
    Mixin for optimized database queries
    Automatically handles select_related and prefetch_related
    """
    
    def get_queryset(self):
        """Override to add optimizations"""
        qs = super().get_queryset()
        
        # Add select_related for ForeignKey fields
        if hasattr(self, 'select_related_fields'):
            qs = qs.select_related(*self.select_related_fields)
        
        # Add prefetch_related for ManyToMany fields
        if hasattr(self, 'prefetch_related_fields'):
            qs = qs.prefetch_related(*self.prefetch_related_fields)
        
        # Only fetch required fields
        if hasattr(self, 'only_fields'):
            qs = qs.only(*self.only_fields)
        
        return qs


def bulk_create_optimized(model_class, data_list, batch_size=1000):
    """
    Optimized bulk creation - handles large datasets efficiently
    """
    objects_to_create = [model_class(**data) for data in data_list]
    
    # Create in batches to avoid memory issues
    created = []
    for i in range(0, len(objects_to_create), batch_size):
        batch = objects_to_create[i:i + batch_size]
        created.extend(model_class.objects.bulk_create(batch, ignore_conflicts=True))
    
    logger.info(f"Bulk created {len(created)} {model_class.__name__} objects")
    return created


# ==================== PERFORMANCE MONITORING ====================

def track_performance(func):
    """
    Decorator to log API performance
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        if execution_time > 1.0:  # Log slow queries
            logger.warning(
                f"SLOW API: {func.__name__} took {execution_time:.2f}s"
            )
        else:
            logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
        
        return result
    return wrapper


# ==================== PAGINATION OPTIMIZATION ====================

class OptimizedPagination:
    """
    Cursor-based pagination for better performance on large datasets
    """
    
    @staticmethod
    def paginate(queryset, cursor=None, page_size=50):
        """
        Returns paginated results with cursor
        """
        if cursor:
            queryset = queryset.filter(id__gt=cursor)
        
        results = list(queryset[:page_size + 1])
        
        has_next = len(results) > page_size
        if has_next:
            results = results[:page_size]
        
        next_cursor = results[-1].id if has_next and results else None
        
        return {
            'results': results,
            'next_cursor': next_cursor,
            'has_next': has_next
        }


# ==================== RESPONSE OPTIMIZATION ====================

def optimize_serializer_response(serializer_class, queryset, many=True):
    """
    Optimized serialization with selective field loading
    """
    # Only serialize required fields
    serializer = serializer_class(
        queryset,
        many=many,
        context={'request': None}  # Avoid unnecessary request context
    )
    return serializer.data


# ==================== AGGREGATION HELPERS ====================

class AggregationHelper:
    """
    Optimized aggregation queries
    """
    
    @staticmethod
    def get_stats(model, filters=None, group_by=None):
        """
        Generic stats calculator with grouping
        """
        qs = model.objects.all()
        
        if filters:
            qs = qs.filter(**filters)
        
        if group_by:
            return qs.values(group_by).annotate(
                count=Count('id'),
                total=Sum('amount')  # Customize as needed
            )
        
        return qs.aggregate(
            count=Count('id'),
            total=Sum('amount')
        )
    
    @staticmethod
    def monthly_trend(model,date_field, value_field, months=6):
        """
        Get monthly trend data efficiently
        """
        from django.db.models.functions import TruncMonth
        from datetime import datetime, timedelta
        
        start_date = datetime.now() - timedelta(days=30 * months)
        
        return model.objects.filter(
            **{f'{date_field}__gte': start_date}
        ).annotate(
            month=TruncMonth(date_field)
        ).values('month').annotate(
            total=Sum(value_field),
            count=Count('id')
        ).order_by('month')


# ==================== CONCURRENT REQUEST HANDLING ====================

from concurrent.futures import ThreadPoolExecutor
import asyncio

class ParallelAPIHelper:
    """
    Execute multiple API calls in parallel
    """
    
    @staticmethod
    def fetch_parallel(api_calls):
        """
        Execute multiple API endpoints in parallel
        api_calls: list of (function, args, kwargs) tuples
        """
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(func, *args, **kwargs)
                for func, args, kwargs in api_calls
            ]
            
            results = [future.result() for future in futures]
        
        return results


# ==================== DATABASE CONNECTION POOLING ====================

"""
Add to settings.py for production:

DATABASES = {
    'default': {
        ...
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'  # 30s query timeout
        }
    }
}
"""


# ==================== MIDDLEWARE FOR PERFORMANCE ====================

class PerformanceMonitoringMiddleware:
    """
    Middleware to track request/response times
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # Log slow requests
        if duration > 2.0:
            logger.warning(
                f"SLOW REQUEST: {request.method} {request.path} took {duration:.2f}s"
            )
        
        # Add performance header
        response['X-Response-Time'] = f"{duration:.3f}s"
        
        return response


# ==================== USAGE EXAMPLES ====================

"""
EXAMPLE 1: Optimized View with Caching

class StudentListAPI(OptimizedQueryMixin, APIView):
    select_related_fields = ['class_assigned', 'created_by']
    prefetch_related_fields = ['courses', 'live_classes', 'marketing', 'leads', 'batches', 'enrollments', 'lms_materials', 'exams']
    only_fields = ['id', 'name', 'roll_number']
    
    @track_performance
    @cache_api_response(timeout=300)
    def get(self, request):
        students = self.get_queryset()
        data = optimize_serializer_response(StudentSerializer, students)
        return Response(data)


EXAMPLE 2: Bulk Operations

# Instead of:
for data in student_data:
    Student.objects.create(**data)  # N queries!

# Use:
bulk_create_optimized(Student, student_data, batch_size=500)  # 1 query!


EXAMPLE 3: Parallel API Calls

api_calls = [
    (get_students, (), {}),
    (get_attendance, (), {}),
    (get_grades, (), {})
]

results = ParallelAPIHelper.fetch_parallel(api_calls)
students, attendance, grades = results


EXAMPLE 4: Aggregation

stats = AggregationHelper.get_stats(
    Payment,
    filters={'status': 'PAID'},
    group_by='payment_type'
)
"""
