from rest_framework import permissions


class IsAdminOrManager(permissions.BasePermission):
    """
    Custom permission to only allow admins or managers to perform an action.
    """
    
    def has_permission(self, request, view):
        return request.user and (request.user.role == 'ADMIN' or request.user.role == 'MANAGER')


class IsAdminOrManagerOrOwner(permissions.BasePermission):
    """
    Custom permission to only allow admins, managers, or the owner of an object to perform an action.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if user is admin or manager
        if request.user.role == 'ADMIN' or request.user.role == 'MANAGER':
            return True
        
        # Check if this is the user's own object
        if hasattr(obj, 'user_id'):
            return obj.user_id == request.user.id
        return obj.id == request.user.id
