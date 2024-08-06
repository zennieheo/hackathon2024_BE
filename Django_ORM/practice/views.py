import re
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.authtoken.models import Token

from .models import Board, Post, Comment, Image, APIKey, CustomUser, FoodIntake
from .serializers import (
    BoardSerializer,
    PostSerializer,
    CommentSerializer,
    ImageSerializer,
    APIKeySerializer,
    UserSerializer,
    FoodIntakeSerializer,
    RegisterSerializer
)


class IsOwnerOrReadOnly(BasePermission):
    """
    Permission class to allow object owner to edit, and others to read.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return obj.user == request.user


def root_view(request):
    """
    Root view to display a welcome message.
    """
    return JsonResponse({"message": "Welcome to the API!"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, post_id):
    """
    API view to create a comment on a specific post.
    """
    post = get_object_or_404(Post, pk=post_id)
    serializer = CommentSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(user=request.user, post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_api_key_form(request):
    """
    API view to create or retrieve an API key for a user.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user:
        api_key, created = APIKey.objects.get_or_create(user=user)
        serializer = APIKeySerializer(api_key)
        return Response({'api_key': serializer.data['key']}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class BoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving, creating, updating, and deleting boards.
    """
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [AllowAny]


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving, creating, updating, and deleting posts.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Filter posts by board_id if provided.
        """
        board_id = self.request.query_params.get('board_id')
        if board_id:
            return self.queryset.filter(board_id=board_id)
        return self.queryset

    def perform_create(self, serializer):
        """
        Save the post with the current user.
        """
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create a post and associated images.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(user=request.user)

        files = request.FILES.getlist('images')
        for file in files:
            Image.objects.create(post=post, image=file)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """
        Update a post and manage images.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()

        files = request.FILES.getlist('images')
        for file in files:
            Image.objects.create(post=post, image=file)

        image_ids_to_delete = request.data.get('delete_images', [])
        for image_id in image_ids_to_delete:
            Image.objects.filter(id=image_id).delete()

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving, creating, updating, and deleting comments.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        """
        Save the comment with the current user.
        """
        serializer.save(user=self.request.user)


class ImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving, creating, updating, and deleting images.
    """
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class PostDetailAPIView(APIView):
    """
    API view to retrieve a specific post and its comments.
    """
    permission_classes = [AllowAny]

    def get(self, request, board_id, post_id):
        post = get_object_or_404(Post, pk=post_id)
        post_serializer = PostSerializer(post)
        comments = post.comments.all()
        comment_serializer = CommentSerializer(comments, many=True)

        return Response({
            "post": post_serializer.data,
            "comments": comment_serializer.data,
        })


class RegisterAPI(generics.GenericAPIView):
    """
    API view to register a new user and return a token.
    """
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token.key,
        })


class user_login(APIView):
    """
    API view to authenticate a user and return a token.
    """
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class user_logout(APIView):
    """
    API view to log out a user by deleting their token.
    """
    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class get_profile(APIView):
    """
    API view to retrieve the profile of the currently authenticated user.
    """
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class update_required_intake(APIView):
    """
    API view to update the required intake of the currently authenticated user.
    """
    def patch(self, request, *args, **kwargs):
        user = request.user
        required_intake = request.data.get('required_intake')

        if required_intake is not None:
            user.required_intake = required_intake
            user.save()
            return Response({'message': 'Required intake updated successfully.'}, status=status.HTTP_200_OK)

        return Response({'error': 'Required intake not provided.'}, status=status.HTTP_400_BAD_REQUEST)


class FoodIntakeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating, and deleting food intake records.
    """
    permission_classes = [IsAuthenticated]

    def format_decimal(self, value):
        """
        Format Decimal values to two decimal places.
        """
        if value is None:
            return '0.00'
        return str(Decimal(value).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))

    def calculate_totals(self, user, date):
        """
        Calculate total intake for each meal and the daily total.
        """
        meal_totals = FoodIntake.objects.filter(user=user, date=date).values('meal_time').annotate(
            total_calories=Sum('calories'),
            total_carbs=Sum('carbs'),
            total_protein=Sum('protein'),
            total_fat=Sum('fat')
        )

        daily_totals = FoodIntake.objects.filter(user=user, date=date).aggregate(
            total_calories=Sum('calories'),
            total_carbs=Sum('carbs'),
            total_protein=Sum('protein'),
            total_fat=Sum('fat')
        )

        meal_totals_dict = {
            meal['meal_time']: {
                'total_calories': self.format_decimal(meal['total_calories']),
                'total_carbs': self.format_decimal(meal['total_carbs']),
                'total_protein': self.format_decimal(meal['total_protein']),
                'total_fat': self.format_decimal(meal['total_fat'])
            } for meal in meal_totals
        }

        meal_totals_dict['daily'] = {
            'total_calories': self.format_decimal(daily_totals['total_calories']),
            'total_carbs': self.format_decimal(daily_totals['total_carbs']),
            'total_protein': self.format_decimal(daily_totals['total_protein']),
            'total_fat': self.format_decimal(daily_totals['total_fat'])
        }

        meal_totals_dict['date'] = date

        return meal_totals_dict

    def create(self, request):
        """
        Create a new food intake record and return totals for the specified date.
        """
        serializer = FoodIntakeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            date = request.data.get('date')
            if not date:
                return Response({"detail": "Date is required."}, status=status.HTTP_400_BAD_REQUEST)

            meal_totals_dict = self.calculate_totals(request.user, date)
            return Response(meal_totals_dict, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        """
        List food intake records and totals for a specific date.
        """
        date = request.query_params.get('date')
        if not date:
            return Response({"detail": "Date parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not re.match(r'\d{4}-\d{2}-\d{2}', date):
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        meal_totals_dict = self.calculate_totals(request.user, date)
        return Response(meal_totals_dict, status=status.HTTP_200_OK)

    def destroy(self, request):
        """
        Delete all food intake records for the current user.
        """
        deleted_count, _ = FoodIntake.objects.filter(user=request.user).delete()
        
        if deleted_count > 0:
            return Response({'message': 'All food intake data has been successfully deleted.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'No data to delete.'}, status=status.HTTP_404_NOT_FOUND)
