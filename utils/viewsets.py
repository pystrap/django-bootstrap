from operator import itemgetter

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from mailer.models import Notification
from mailer.serializers import NotificationSerializer


class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class AdminToolsViewSet(viewsets.ViewSet):
    permission_classes = (IsSuperUser,)

    @action(methods=["get"], url_path="test",
            detail=False, url_name="test")
    def test(self, request):
        return Response({'success': 'success'})


class AccountViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    @action(methods=["get"], url_path="notifications",
            detail=False, url_name="notifications")
    def notifications(self, request):
        notes = []
        notifications = Notification.objects.select_related('user', 'from_user').filter(
            user=request.user, seen=False),
        notifications_paginator = LimitOffsetPagination()
        notifications_paginated = notifications_paginator.paginate_queryset(notifications, request)
        if int(request.query_params.get('offset', 0)) == 0:
            query_meta['notifications'] = {
                'count': notifications_paginator.count,
                'next': notifications_paginator.get_next_link(),
                'previous': notifications_paginator.get_previous_link(),
            }
        for e in NotificationSerializer(notifications_paginated, many=True).data:
            n = {
                **e,
                'id': e['id'],
                'type': e['type'],
                'object': e['object'],
                'objectId': e['object_id'],
                'action': e['action'],
                'message': e['message'],
                'date': e['created_at'],
                'data': e['data'],
            }
            notes.append(n)
        response = {
            'status': 'ok',
            'notifications': sorted(notes, key=itemgetter('date'), reverse=True),
            'meta': query_meta,
        }
        # fetch new messages
        return Response(response)

    @action(methods=["put"], url_path="read_notification",
            detail=True, url_name="read_notification")
    def read_notification(self, request, pk=None):
        notification = get_object_or_404(Notification, pk=pk)
        if notification.user != request.user:
            raise PermissionDenied({"message": "Not allowed!"})
        notification.seen = True
        notification.save()
        return Response({'success': 'success'})

    @action(methods=["put"], url_path="dismiss_all_notifications",
            detail=False, url_name="dismiss_all_notifications")
    def dismiss_all_notifications(self, request):
        request.user.notifications.filter(seen=False).update(seen=True)
        return Response({'success': 'success'})


