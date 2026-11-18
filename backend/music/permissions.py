from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrPublicReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.is_public or obj.owner_id == request.user.id
        return request.user.is_authenticated and obj.owner_id == request.user.id
