"""
Soft Delete Utility for Y.S.M AI
Provides optional soft delete functionality without breaking existing code
"""

from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """
    Manager to exclude soft-deleted objects by default
    Usage: objects = SoftDeleteManager()
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    """
    Abstract base model that adds soft delete functionality
    
    Usage:
        class MyModel(SoftDeleteModel):
            name = models.CharField(max_length=100)
            # ... other fields
    
    This provides:
    - is_deleted field
    - deleted_at timestamp
    - soft_delete() method
    - restore() method
    - SoftDeleteManager as default manager
    - all_objects manager (includes deleted)
    """
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Default manager excludes deleted objects
    objects = SoftDeleteManager()
    
    # Manager that includes deleted objects
    all_objects = models.Manager()
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        """Soft delete this instance"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])
    
    def restore(self):
        """Restore a soft-deleted instance"""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])
    
    def delete(self, using=None, keep_parents=False, hard=False):
        """
        Override delete to use soft delete by default
        Use hard=True for permanent deletion
        """
        if hard:
            return super().delete(using=using, keep_parents=keep_parents)
        else:
            self.soft_delete()


# Example usage in existing models (OPTIONAL - Don't apply yet):
"""
# BEFORE:
class Student(models.Model):
    name = models.CharField(max_length=100)
    # ... fields

# AFTER (when you want soft delete):
class Student(SoftDeleteModel):  # Inherit from SoftDeleteModel
    name = models.CharField(max_length=100)
    # ... fields
    # is_deleted and deleted_at fields automatically added
"""
