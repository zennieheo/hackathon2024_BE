from django.contrib import admin
from .models import Board, Post, Comment, Image

admin.site.register(Board)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Image)