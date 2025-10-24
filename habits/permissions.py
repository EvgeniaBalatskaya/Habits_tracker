from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Владелец может делать всё, остальные — только чтение (если запись публична и view предназначен для публичного списка).
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request if habit is public
        if request.method in permissions.SAFE_METHODS and getattr(obj, "is_public", False):
            return True
        # Otherwise only owner can modify / view private
        return obj.owner == request.user
