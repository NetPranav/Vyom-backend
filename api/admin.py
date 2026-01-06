from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Task, Offer, ChatMessage, Transaction

# 1. Custom User Admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Locals Info', {'fields': ('is_verified', 'is_student', 'phone_number', 'skills', 'trust_score', 'rating')}),
        ('Financials', {'fields': ('wallet_balance', 'total_earnings', 'active_gigs_count')}),
    )
    list_display = ['username', 'email', 'phone_number', 'is_student', 'trust_score']

# 2. Task Admin
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'budget', 'created_by', 'priority', 'deadline']
    list_filter = ['status', 'priority', 'tags']
    search_fields = ['title', 'description', 'location_string']

# 3. Offer Admin
@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['task', 'helper', 'price_bid', 'status', 'created_at']
    list_filter = ['status']

# 4. Other Models
admin.site.register(ChatMessage)
admin.site.register(Transaction)