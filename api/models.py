from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from decimal import Decimal
# ==========================================
# 1. USER & PROFILE
# ==========================================
class User(AbstractUser):
    # Identity
    is_verified = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    avatar = models.URLField(max_length=500, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, help_text="Primary account phone")
    
    # Helper Stats
    skills = models.TextField(help_text="Tags: 'Plumbing, Math, Coding'", blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    trust_score = models.IntegerField(default=100)
    
    # Money
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    active_gigs_count = models.IntegerField(default=0)

    def __str__(self):
        return self.username

# ==========================================
# 2. THE TASK
# ==========================================
class Task(models.Model):
    # -- Enums --
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired')
    ]

    PRIORITY_CHOICES = [
        ('STANDARD', 'Standard'),
        ('URGENT', 'Urgent (Red Border)'), 
    ]

    # -- Core Task Info --
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.URLField(max_length=500, null=True, blank=True)
    
    # FIX 1: Added default='' so migration doesn't crash on existing rows
    tags = models.CharField(
        max_length=100, 
        default='', 
        help_text="e.g. 'Plumbing', 'Dog Walking', 'Queue Standing'"
    )
    
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='STANDARD')
    
    # -- Contact Details --
    # FIX 2: Added default='' to allow migration. 
    # Logic: New tasks must provide it, old tasks (if any) will have empty string.
    contact_email = models.EmailField(
        help_text="Email for this specific task", 
        default='' 
    )
    
    # FIX 3: Added default=''
    primary_phone = models.CharField(
        max_length=15, 
        help_text="Main contact number", 
        default=''
    )
    
    secondary_phone = models.CharField(max_length=15, blank=True, null=True, help_text="Backup number (optional)")

    # -- Money & Time --
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=4, decimal_places=2, default=0.12)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # FIX 4: Added default='1 Hour' so migration doesn't crash
    estimated_duration = models.CharField(
        max_length=50, 
        help_text="e.g., '30 mins', '2 hours'", 
        default='1 Hour'
    )
    
    deadline = models.DateTimeField()

    # -- Location --
    latitude = models.FloatField()
    longitude = models.FloatField()
    location_string = models.CharField(max_length=255, help_text="e.g., 'Block A, Indirapuram'")

    # -- Metadata --
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    
    # -- Relationships --
    created_by = models.ForeignKey(User, related_name='created_tasks', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, related_name='assigned_tasks', null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        # Calculate commission (12%)
        # FIX: Convert the float (0.12) to a Decimal before multiplying
        self.commission_rate = 0.12 
        self.commission_amount = self.budget * Decimal(str(self.commission_rate))
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.status})"

# ==========================================
# 3. OFFERS
# ==========================================
class Offer(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected')]
    task = models.ForeignKey(Task, related_name='offers', on_delete=models.CASCADE)
    helper = models.ForeignKey(User, related_name='offers_made', on_delete=models.CASCADE)
    message = models.TextField()
    price_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('task', 'helper')

# ==========================================
# 4. CHAT & TRANSACTIONS
# ==========================================
class ChatMessage(models.Model):
    task = models.ForeignKey(Task, related_name='chat_messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):
    TRANSACTION_TYPES = [('CREDIT', 'Credit'), ('DEBIT', 'Debit'), ('WITHDRAWAL', 'Withdrawal')]
    user = models.ForeignKey(User, related_name='transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)