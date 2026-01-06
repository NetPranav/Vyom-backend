from rest_framework import serializers
from .models import User, Task, Offer, ChatMessage, Transaction

# 1. User Serializer (Updated)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 
            'is_student', 'is_verified', 'rating', 'trust_score', 'avatar',
            'phone_number', 'skills', 'wallet_balance'
        ]
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ['rating', 'trust_score', 'wallet_balance'] # User can't edit these

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            is_student=validated_data.get('is_student', False),
            phone_number=validated_data.get('phone_number', '')
        )
        return user

# 2. Offer Serializer
class OfferSerializer(serializers.ModelSerializer):
    helper_name = serializers.ReadOnlyField(source='helper.username')
    helper_rating = serializers.ReadOnlyField(source='helper.rating')
    helper_avatar = serializers.ImageField(source='helper.avatar', read_only=True)

    class Meta:
        model = Offer
        fields = ['id', 'task', 'helper', 'helper_name', 'helper_rating', 'helper_avatar', 'price_bid', 'message', 'status', 'created_at']
        read_only_fields = ['helper', 'status']

# 3. Task Serializer
class TaskSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.username')
    created_by_avatar = serializers.ImageField(source='created_by.avatar', read_only=True)
    offers = OfferSerializer(many=True, read_only=True) # Show bids inside task details

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'image', 'tags', 'priority', 
            'contact_email', 'primary_phone', 'secondary_phone',
            'budget', 'commission_amount', 'estimated_duration', 'deadline',
            'latitude', 'longitude', 'location_string',
            'status', 'created_by', 'created_by_name', 'created_by_avatar', 'assigned_to', 'offers',
            'created_at'
        ]
        read_only_fields = ['created_by', 'commission_amount', 'assigned_to', 'status']