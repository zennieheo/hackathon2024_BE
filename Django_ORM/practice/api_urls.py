from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BoardViewSet,
    PostViewSet,
    CommentViewSet,
    ImageViewSet,
    create_api_key
)

# DRF DefaultRouter 설정
router = DefaultRouter()
router.register(r'boards', BoardViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'images', ImageViewSet)

urlpatterns = [
    # API Key 생성 경로
    path('create-api-key/', create_api_key, name='create_api_key'),
    
    # DRF ViewSet 경로 포함
    path('', include(router.urls)),
]
