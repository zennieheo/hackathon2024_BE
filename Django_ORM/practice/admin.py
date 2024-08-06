from django.contrib import admin
from .models import Board, Post, Comment, Image, CustomUser



admin.site.register(Board)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Image)

"""
# customuser 모델을 관리자 패널에 등록 ___ added!
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'name', 'activity_level', 'height', 'weight')
    search_fields = ('usernmae', 'email', 'name')



"""

