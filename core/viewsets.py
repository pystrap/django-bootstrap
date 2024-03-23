from django.contrib.admin.models import CHANGE
from django.contrib.auth import get_user_model
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Note
from .serializers import NoteSerializer, UserInfoSerializer, UserAccountSerializer, LoginSerializer, \
    ChangePasswordSerializer

User = get_user_model()


class NotesMixin:
    @action(methods=["post"], detail=True,
            url_path="add_note", url_name="add_note")
    def add_note(self, request, pk=None, log_action=True):
        if not request.user.has_perm("account.add_note"):
            raise PermissionDenied({"message": "You don't have permission to perform operation"})
            return null
        note = request.data.get('note', None)
        if not note:
            raise ValidationError('Please specify notes to add')
        instance = self.get_object()
        note = Note.objects.create(entity=instance, curator=request.user, note=note)
        if log_action:
            instance.log_action(request.user.id, CHANGE,
                                'Added note: ' + str(note), changed_fields=['notes'])
        return Response(NoteSerializer(note).data)

    @action(methods=["put"], detail=True,
            url_path="edit_note", url_name="edit_note")
    def edit_note(self, request, pk=None):
        if not request.user.has_perm("account.change_note"):
            raise PermissionDenied({"message": "You don't have permission to perform operation"})
            return null
        note = get_object_or_404(Note, pk=request.data.get('id'))
        instance = self.get_object()
        if not note.entity == instance:
            raise ValidationError('Note does not belong to entity!')
        instance.log_action(request.user.id, CHANGE,
                            'Updated note: ' + str(note) + ' posted by ' + str(note.curator), changed_fields=['notes'])
        note.note = request.data.get('note')
        note.curator = request.user
        note.save()
        return Response(NoteSerializer(note).data)

    @action(methods=["delete"], detail=True,
            url_path="delete_note", url_name="delete_note")
    def delete_note(self, request, pk=None):
        if not request.user.has_perm("account.delete_note"):
            raise PermissionDenied({"message": "You don't have permission to perform operation"})
            return null
        note = get_object_or_404(Note, pk=request.data.get('id'))
        instance = self.get_object()
        instance.log_action(request.user.id, CHANGE,
                            'Deleted note: ' + str(note), changed_fields=['notes'])
        note.delete()
        return Response(NoteSerializer(note).data)


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    serializer_class = UserInfoSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated']
    ordering = ['-updated']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()

    def get_object(self):
        lookup_field_value = self.kwargs[self.lookup_field]

        obj = User.objects.get(lookup_field_value)
        self.check_object_permissions(self.request, obj)

        return obj

    @action(methods=["GET"], detail=False)
    def account(self, request):
        user = request.user
        return Response(UserAccountSerializer(user).data)


class LoginViewSet(viewsets.ModelViewSet, TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RefreshViewSet(viewsets.ViewSet, TokenRefreshView):
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # # if using drf authtoken, create a new token
        # if hasattr(user, 'auth_token'):
        #     user.auth_token.delete()
        # token, created = Token.objects.get_or_create(user=user)
        # # return new token
        return Response({'success': 'success'}, status=status.HTTP_200_OK)
