from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response


class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class AdminToolsViewSet(viewsets.ViewSet):
    permission_classes = (IsSuperUser,)

    @action(methods=["get"], url_path="test",
            detail=False, url_name="test")
    def test(self, request):
        return Response({'success': 'success'})
