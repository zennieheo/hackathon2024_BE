from django.db import models

class Board(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Post(models.Model):
    board = models.ForeignKey(Board, related_name='posts', on_delete=models.CASCADE)
    author = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    contents = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    images = models.ImageField(upload_to='post_images/', blank=True, null=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author}: {self.content}'
