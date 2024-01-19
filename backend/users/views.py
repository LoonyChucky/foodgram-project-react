from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.serializers import CreateSubscribtionSerializer, SubscriberSerializer
from users.models import User
from utils.paginations import MyPagination


class CustomUserViewSet(UserViewSet):

    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = MyPagination

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(methods=['post'],
            detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        author = User.objects.filter(id=id)
        if not author.exists():
            return Response({'error': 'no such author'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = CreateSubscribtionSerializer(
            data={'user': request.user.id, 'author': id},
            context={'request': request})

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        author = User.objects.filter(id=id)
        if not author.exists():
            return Response({'error': 'no such author'},
                            status=status.HTTP_404_NOT_FOUND)

        subscription = self.request.user.followed_users.filter(author=id)

        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'error': 'no such subscribe'},
            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'],
            detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            author__user=request.user)
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriberSerializer(
            page, many=True, context={'request': request})

        return self.get_paginated_response(serializer.data)
