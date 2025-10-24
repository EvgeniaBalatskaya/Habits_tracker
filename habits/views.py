from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Habit
from .serializers import HabitSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        # owners see their habits (private+public)
        user = self.request.user
        if self.action == "list":
            return Habit.objects.filter(owner=user)
        return Habit.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_done(self, request, pk=None):
        """
        Endpoint: POST /habits/{id}/mark_done/
        установить last_performed = today
        """
        habit = self.get_object()
        if habit.owner != request.user:
            return Response({"detail": "Not allowed"}, status=403)
        habit.last_performed = timezone.now().date()
        habit.save()
        return Response({"status": "ok"})


class PublicHabitListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Только список публичных привычек (read-only)
    """
    queryset = Habit.objects.filter(is_public=True)
    serializer_class = HabitSerializer
    permission_classes = [AllowAny]  # любой пользователь может просматривать список публичных
