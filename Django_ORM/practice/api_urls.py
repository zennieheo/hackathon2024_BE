from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BoardViewSet,
    PostViewSet,
    CommentViewSet,
    ImageViewSet,
    create_api_key_form,
    FoodIntakeViewSet,
)

# DRF DefaultRouter 설정
router = DefaultRouter()
router.register(r'boards', BoardViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'images', ImageViewSet)
router.register(r'food-intake', FoodIntakeViewSet, basename='food-intake')

urlpatterns = [
    # API Key 생성 경로
    path('create-api-key/', create_api_key_form, name='create_api_key_form'),

    # DRF ViewSet 경로 포함
    path('', include(router.urls)),
]
