from django.urls import path
from .views import (
    RegisterView, UserProfileView, LogoutView, 
    TaskCreateView, TaskFeedView, TaskDetailView,
    CreateOfferView, AcceptOfferView,DashboardDataView,ClaimTaskView
)

urlpatterns = [
    # --- Auth ---
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # --- Tasks ---
    path('tasks/create/', TaskCreateView.as_view(), name='create-task'),
    path('tasks/', TaskFeedView.as_view(), name='task-feed'),  # GET /tasks?search=plumbing
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),

    # --- Interaction ---
    path('tasks/<int:task_id>/offer/', CreateOfferView.as_view(), name='make-offer'), # POST to bid
    path('offers/<int:offer_id>/accept/', AcceptOfferView.as_view(), name='accept-offer'), # POST to lock task

    path('dashboard/data/', DashboardDataView.as_view(), name='dashboard-data'),
    path('tasks/<int:pk>/claim/', ClaimTaskView.as_view(), name='claim-task'),
]