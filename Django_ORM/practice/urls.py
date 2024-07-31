from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    path('board/<int:board_id>/', 
         views.board_detail, 
         name='board_detail'),
    
    path('board/<int:board_id>/post/<int:post_id>/', 
         views.post_detail, 
         name='post_detail'),
    
    path('board/<int:board_id>/new_post/', 
         views.new_post, 
         name='new_post'),
    
    path('post/<int:post_id>/edit/', 
         views.edit_post, 
         name='edit_post'),
    
    path('post/<int:post_id>/delete/', 
         views.delete_post, 
         name='delete_post'),

]
