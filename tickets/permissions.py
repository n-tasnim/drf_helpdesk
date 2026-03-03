from rest_framework.permissions import BasePermission

class IsAdminOrOwner(BasePermission):
    """
    - Admin can access everything
    - Normal user can only access their own tickets
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        return obj.created_by == request.user