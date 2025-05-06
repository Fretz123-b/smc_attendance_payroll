from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

# Custom User model (Admin or Employee User)
class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.get_full_name()

# Position model (NEW)
class Position(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Employee model
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField()
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, related_name='employees')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Department model
class Department(models.Model):
    department_name = models.CharField(max_length=100)

    def __str__(self):
        return self.department_name

# Employee-Department Assignment model
class EmployeeDepartment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='departments')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='employees')

    class Meta:
        unique_together = ('employee', 'department')

    def __str__(self):
        return f"{self.employee} - {self.department}"

# Holiday model
class Holiday(models.Model):
    date = models.DateField()
    description = models.TextField()
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,limit_choices_to={'is_admin': True}, related_name="holidays")

    def __str__(self):
        return f"{self.date} - {self.description}"
    
# PayRate model (formerly Pass)
class PayRate(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    pay_rate = models.DecimalField(max_digits=10, decimal_places=2)
    hours_per_day = models.DecimalField(max_digits=4, decimal_places=2, default=8.0)  # Add default here

    def __str__(self):
        return f"PayRate for {self.employee}"

# Payroll model
class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="payrolls")
    pay_period = models.DateField() 
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.employee} - {self.pay_period.strftime('%Y-%m')}"

    def calculate_net_salary(self):
        self.total_deductions = sum(d.salary_deduction for d in self.deductions_set.all())
        self.net_salary = self.gross_salary - self.total_deductions
        self.save()

    class Meta:
        ordering = ['-pay_period']

# Deductions model
class Deductions(models.Model):
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='deductions')
    salary_deduction = models.DecimalField(max_digits=10, decimal_places=2)
    label = models.CharField(max_length=100, default='Other')  
    def __str__(self):
        return f"{self.payroll} - Deduction: {self.salary_deduction}"

# Attendance model
class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="attendances")
    payroll = models.ForeignKey(Payroll, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendances")
    date = models.DateField()
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    total_hours = models.FloatField(null=True, blank=True)
    holiday = models.ForeignKey(Holiday, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if self.time_in and self.time_out:
            duration = datetime.combine(self.date, self.time_out) - datetime.combine(self.date, self.time_in)
            self.total_hours = round(duration.total_seconds() / 3600, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} - {self.date}"

    @property
    def is_holiday(self):
        return self.holiday is not None

    class Meta:
        ordering = ['-date']

# Leave model
class Leave(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="leaves")
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                              limit_choices_to={'is_admin': True}, related_name="approved_leaves")
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.employee} - {self.status}"

    class Meta:
        ordering = ['-start_date']
