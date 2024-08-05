

from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.root_view, name='root'), # http://127.0.0.1:8000/ 첫화면에 뭐라도 뜨라고 만든 건데 지워도 됨...
    path('register/', views.register_user, name='register'),  # 회원가입 엔드포인트
    path('login/', views.user_login, name='login'),          # 로그인 엔드포인트
    path('logout/', views.user_logout, name='logout'),       # 로그아웃 엔드포인트
    path('profile/', views.get_profile, name='profile'),     # 프로필 엔드포인트
    path('api/', include('practice.api_urls')),        # API 경로 포함
]