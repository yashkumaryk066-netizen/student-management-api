from django.db import models
from django.contrib.auth.models import User
from .base import AuditModel

class HRDepartment(AuditModel):
    """Organization departments"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    head_of_department = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
    
    def __str__(self):
        return self.name

class Designation(AuditModel):
    """Job roles/titles"""
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.title

class Employee(AuditModel):
    """Staff and faculty records"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    department = models.ForeignKey(HRDepartment, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, blank=True)
    joining_date = models.DateField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    contract_type = models.CharField(max_length=20, choices=[('PERMANENT', 'Permanent'), ('CONTRACT', 'Contract'), ('VISITING', 'Visiting')])
    bank_account_no = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.designation})"

class LeaveRequest(AuditModel):
    """Employee leave management"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=[('SICK', 'Sick Leave'), ('CASUAL', 'Casual Leave'), ('EARNED', 'Earned Leave')])
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    
    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.status})"

class Payroll(AuditModel):
    """Staff salary processing"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    month = models.CharField(max_length=20) # e.g. "January 2025"
    year = models.IntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('PAID', 'Paid'), ('PENDING', 'Pending')], default='PENDING')
    transaction_id = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.employee} - {self.month} {self.year}"
    
    def save(self, *args, **kwargs):
        self.net_salary = self.basic_salary + self.allowances - self.deductions
        super().save(*args, **kwargs)
