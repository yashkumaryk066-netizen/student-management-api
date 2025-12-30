from django.db import models
from django.contrib.auth.models import User
from student.models import Student

class Employee(models.Model):
    """Staff/Employee Details"""
    EMP_TYPES = [
        ('TEACHING', 'Teaching Staff'),
        ('NON_TEACHING', 'Non-Teaching Staff'),
        ('ADMIN', 'Administrative'),
        ('SUPPORT', 'Support Staff'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    emp_type = models.CharField(max_length=20, choices=EMP_TYPES)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    joining_date = models.DateField()
    bank_account_no = models.CharField(max_length=50)
    pan_number = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.designation}"

class Payroll(models.Model):
    """Employee Salary Processing"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.DateField()  # 1st of every month
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, default='PENDING', choices=[('PENDING', 'Pending'), ('PROCESSED', 'Processed')])
    payment_date = models.DateField(null=True)
    
    class Meta:
        unique_together = ['employee', 'month']

class Expense(models.Model):
    """Institutional Expenses"""
    EXPENSE_TYPES = [
        ('UTILITY', 'Electricity/Water/Internet'),
        ('MAINTENANCE', 'Maintenance/Repairs'),
        ('PURCHASE', 'Assets/Inventory Purchase'),
        ('SALARY', 'Salary Payments'),
        ('EVENT', 'Event Expenses'),
        ('OTHER', 'Miscellaneous'),
    ]
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_expenses')
    receipt_url = models.URLField(blank=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.title} - ₹{self.amount}"
