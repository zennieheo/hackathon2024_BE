from django.urls import path, include
from .views import root_view, RegisterAPI, user_login, user_logout, get_profile


urlpatterns = [
    path('', root_view, name='root'),  # 첫화면 엔드포인트
    path('register/', RegisterAPI.as_view(), name='register'),  # 회원가입 엔드포인트
    path('login/', user_login.as_view(), name='login'),          # 로그인 엔드포인트
    path('logout/', user_logout.as_view(), name='logout'),       # 로그아웃 엔드포인트
    path('profile/', get_profile.as_view(), name='profile'),     # 프로필 엔드포인트
    
    # API 경로 포함
    path('api/', include('practice.api_urls')),       
]
