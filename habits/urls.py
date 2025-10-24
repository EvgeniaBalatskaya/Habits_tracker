from rest_framework.routers import DefaultRouter
from .views import HabitViewSet, PublicHabitListViewSet

router = DefaultRouter()
router.register(r"habits", HabitViewSet, basename="habit")
router.register(r"public-habits", PublicHabitListViewSet, basename="public-habits")

urlpatterns = router.urls
