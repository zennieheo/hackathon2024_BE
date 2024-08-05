from rest_framework import serializers
from .models import Board, Post, Comment, Image, APIKey, CustomUser, FoodIntake, CustomUser


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['key']




class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'activity_level', 'height', 'weight', 'username', 'password', 'required_intake']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            name=validated_data['name'],
            activity_level=validated_data['activity_level'],
            height=validated_data['height'],
            weight=validated_data['weight'],
            required_intake=validated_data['required_intake'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'activity_level', 'height', 'weight', 'username', 'password', 'required_intake']
        
    

class FoodIntakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodIntake
        fields = ['date', 'meal_time', 'calories', 'carbs', 'protein', 'fat']
        read_only_fields = ['user']
