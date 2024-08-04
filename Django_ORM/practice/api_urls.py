from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView 
from .views import (
    BoardViewSet,
    PostViewSet,
    CommentViewSet,
    ImageViewSet,
    ProtectedView,
    create_api_key_form,
)

# DRF DefaultRouter 설정
router = DefaultRouter()
router.register(r'boards', BoardViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'images', ImageViewSet)

urlpatterns = [
    # API Key 생성 경로
    path('create-api-key/', create_api_key_form, name='create_api_key_form'),
    
    # DRF ViewSet 경로 포함
    path('', include(router.urls)),

    # JWT 인증 관련 URL
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', ProtectedView.as_view(), name='protected_view'),
]