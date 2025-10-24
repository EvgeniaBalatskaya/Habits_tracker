from rest_framework import viewsets, mixins, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Habit
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import HabitSerializer
from .pagination import HabitPagination

class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    pagination_class = HabitPagination

    def get_queryset(self):
        user = self.request.user
        if self.action == 'list_public':
            return Habit.objects.filter(is_public=True)
        return Habit.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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
