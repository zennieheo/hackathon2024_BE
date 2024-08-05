from django.db import models
from django.utils import timezone
import uuid
from django.contrib.auth.models import AbstractUser 




class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, default='example@example.com')  # 기본값 설정
    name = models.CharField(max_length=30, default='Unknown')  # 기본값 설정
    ACTIVITY_LEVEL_CHOICES = [
        (25, '25'),
        (30, '30'),
        (35, '35'),
        (40, '40'),
    ]
    activity_level = models.IntegerField(choices=ACTIVITY_LEVEL_CHOICES, default=25)  # 활동량
    height = models.FloatField(default=170.0)  # 기본값 설정
    weight = models.FloatField(default=70.0)   # 기본값 설정
    required_intake = models.FloatField(null=True, blank=True)  # 권장 섭취량


    def __str__(self):
        return self.username


class APIKey(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f'API Key for {self.user.username}'


class Board(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Post(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title




class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:20]

class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Image {self.id} for post {self.post.title}'





class FoodIntake(models.Model):
      
        MEAL_TIMES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
        
        user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
        calories = models.FloatField()
        carbs = models.FloatField()
        protein = models.FloatField()
        meal_time = models.CharField(max_length=10, choices=MEAL_TIMES) 
        fat = models.FloatField()
        date = models.DateField(auto_now_add=True) 

        def __str__(self):
          return f"{self.food_name} by {self.user.username} on {self.date}"