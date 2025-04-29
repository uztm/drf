from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsOwnerMatchingUsername(BasePermission):
    """
    Permission to only allow users to access their own data based on username and/or id.
    """

    def has_permission(self, request, view):
        username = request.query_params.get('username')
        user_id = request.query_params.get('id') or request.query_params.get('user_id')

        if not username:
            return False

        # Faqat token user va query'dagi username (va agar kerak bo'lsa id) bir xil bo'lsa ruxsat beriladi
        if request.user.username != username:
            return False

        if user_id:
            try:
                return str(request.user.id) == str(user_id)
            except ValueError:
                return False

        return True

class IsStaffOrSuperUser(permissions.BasePermission):
    """
    Custom permission to only allow access to staff or superuser.
    """

    def has_permission(self, request, view):
        # Check if the user is staff or a superuser
        return request.user and (request.user.is_staff or request.user.is_superuser)