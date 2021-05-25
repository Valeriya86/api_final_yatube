
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters, mixins

from .models import Post, Group
from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import (
    FollowSerializer, GroupSerializer, PostSerializer, CommentSerializer,
)


class BaseViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    pass


class PostViewSet(viewsets.ModelViewSet):

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnlyPermission]
    queryset = Post.objects.all()

    filter_backends = [DjangoFilterBackend]
    filter_fields = ['group']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(BaseViewSet):

    queryset = Group.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):

    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnlyPermission
    ]

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs['id'])
        queryset = post.comments.all()
        return queryset

    def perform_create(self, serializer):
        get_object_or_404(Post, id=self.kwargs['id'])
        serializer.save(author=self.request.user)


class FollowViewSet(BaseViewSet):
    serializer_class = FollowSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username']

    def get_queryset(self):
        queryset = self.request.user.following.all()
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
