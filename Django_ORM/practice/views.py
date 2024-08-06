from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Board, Post, Comment
from .serializers import BoardSerializer, PostSerializer, CommentSerializer

from django.shortcuts import get_object_or_404


class BoardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def retrieve(self, request, *args, **kwargs):
        # 게시판의 상세 정보를 반환하면서 게시판에 속한 게시글도 포함
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        posts = Post.objects.filter(board=instance)
        post_serializer = PostSerializer(posts, many=True)
        data = serializer.data
        data['posts'] = post_serializer.data
        return Response(data)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # URL 경로에서 게시판 ID를 가져와서 필터링합니다.
        board_id = self.kwargs.get('board_id')
        if board_id is not None:
            queryset = queryset.filter(board_id=board_id)
        return queryset

    def perform_create(self, serializer):
        board_id = self.kwargs.get('board_id')
        # board_id = self.request.data.get('board_id')
        if board_id:
            serializer.save(board_id=board_id)
        else:
            # 게시판 ID가 없는 경우 오류를 반환합니다.
            raise ValueError("게시판 ID를 제공해야 합니다.")
        
    
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
