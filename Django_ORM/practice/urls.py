from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BoardViewSet, PostViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'boards', BoardViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('boards/<int:board_id>/posts/', PostViewSet.as_view({'get': 'list', 'post': 'create'}), name='board-posts'),
]
