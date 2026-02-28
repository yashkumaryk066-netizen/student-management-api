from django.db import models
from django.contrib.auth.models import User

class AuditModel(models.Model):
    """
    Abstract base class that provides self-updating
    'created_at' and 'updated_at' fields.
    Also tracks who created the record.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='%(class)s_created', 
        null=True, 
        blank=True,
        help_text="User who created this record"
    )

    class Meta:
        abstract = True
