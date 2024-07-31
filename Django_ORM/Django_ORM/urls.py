from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# from rest_framework import permissions ______ unused

# Spectacular Document API URL 패턴
from drf_spectacular.views import SpectacularAPIView, SpectacularJSONAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path('admin/', admin.site.urls),

    # API URLs
    path('api/', include('practice.api_urls')), # practice/api_urls.py를 포함하여 API URL 설정
    
    # Template view URLs
    path('', include('practice.urls')), # practice/urls.py를 포함하여 일반 웹 페이지 URL 설정

    # Spectacular Document API URL 패턴
    path("docs/json/", SpectacularJSONAPIView.as_view(), name="schema-json"),  # JSON 형식의 API 스키마를 제공하는 URL
    path('schema/', SpectacularAPIView.as_view(), name='schema'),  # API 스키마의 기본 URL
    path('schema/user', SpectacularAPIView.as_view(), name='user_schema'),  # 사용자 정의 스키마 URL
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # Swagger UI를 통해 API 문서를 시각화하는 URL
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # ReDoc을 통해 API 문서를 시각화하는 URL

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)