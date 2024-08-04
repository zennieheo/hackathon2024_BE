from django.urls import path
from . import views
from .views import *
# from .views import register_user, user_login, user_logout, FoodIntakeView, get_profile


urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', get_profile, name='get_profile'),
    path('food-intake/', FoodIntakeView.as_view(), name='food-intake'), #ayyyyyyyyyyyyayyyyyyyyyyy


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


