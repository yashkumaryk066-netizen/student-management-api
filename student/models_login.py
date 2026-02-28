
class LoginAttempt(models.Model):
    """
    SECURITY: Track all login attempts for Brute Force Protection & Auditing
    """
    username = models.CharField(max_length=255, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('SUCCESS', 'Success'), ('FAILURE', 'Failure'), ('LOCKED', 'Locked')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} - {self.status} ({self.created_at})"
