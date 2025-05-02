from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_staff or obj.owner == request.user


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
