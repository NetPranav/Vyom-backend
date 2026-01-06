from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, TaskSerializer, OfferSerializer
from .models import User, Task, Offer
from rest_framework import serializers

# =======================
# AUTH VIEWS
# =======================
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# =======================
# TASK VIEWS
# =======================

# 1. Create a Task (Authenticated Users only)
class TaskCreateView(generics.CreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Auto-assign the "Created By" field to the logged-in user
        serializer.save(created_by=self.request.user)

# 2. The Feed (List all OPEN tasks)
class TaskFeedView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Task.objects.filter(status='OPEN').order_by('-created_at')
    
    # Add Search & Filter (e.g., ?search=plumbing)
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'tags', 'location_string']

# 3. Task Detail (See one task + its offers)
class TaskDetailView(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

# =======================
# OFFER & ACCEPTANCE VIEWS
# =======================

# 1. Make an Offer (Bid)
class CreateOfferView(generics.CreateAPIView):
    serializer_class = OfferSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, pk=task_id)
        
        # Validation: User cannot bid on their own task
        if task.created_by == self.request.user:
            raise serializers.ValidationError("You cannot bid on your own task.")
            
        serializer.save(helper=self.request.user, task=task)

# 2. Accept an Offer (The "Lock" Logic)
class AcceptOfferView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, offer_id):
        offer = get_object_or_404(Offer, id=offer_id)
        task = offer.task

        # 1. Security Check: Only the Task Creator can accept
        if task.created_by != request.user:
            return Response({"error": "Not your task"}, status=403)

        # 2. Logic: Update Task Status -> ASSIGNED
        task.assigned_to = offer.helper
        task.status = 'ASSIGNED'
        task.save()

        # 3. Logic: Update Offer Status -> ACCEPTED
        offer.status = 'ACCEPTED'
        offer.save()

        # 4. Reject all other offers for this task (Optional but clean)
        other_offers = Offer.objects.filter(task=task).exclude(id=offer.id)
        other_offers.update(status='REJECTED')

        return Response({"message": f"Task assigned to {offer.helper.username}"}, status=200)

class DashboardDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # 1. User Details
        user_data = UserSerializer(user).data

        # 2. Gigs Accepted by User (Where they are the helper)
        assigned_tasks = Task.objects.filter(assigned_to=user).order_by('-updated_at')
        assigned_serializer = TaskSerializer(assigned_tasks, many=True)

        # 3. Gigs Posted by User (Where they are the creator)
        created_tasks = Task.objects.filter(created_by=user).order_by('-created_at')
        created_serializer = TaskSerializer(created_tasks, many=True)

        return Response({
            "user_profile": user_data,
            "accepted_gigs": assigned_serializer.data,
            "posted_gigs": created_serializer.data
        })


# ... existing imports ...

# NEW: Allow a Helper to claim an OPEN task instantly
class ClaimTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)

        # 1. Validation
        if task.status != 'OPEN':
            return Response({"error": "This gig is no longer available."}, status=400)
        
        if task.created_by == request.user:
            return Response({"error": "You cannot accept your own task."}, status=400)

        # 2. Assign the Task
        task.assigned_to = request.user
        task.status = 'ASSIGNED'
        task.save()

        return Response({"message": "Gig Accepted! Check your Dashboard."}, status=200)