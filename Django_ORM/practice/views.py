import re
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.models import User #customuser?
from django.http import JsonResponse # added
import uuid

from .models import Board, Post, Comment, Image, APIKey, CustomUser, FoodIntake
from .serializers import BoardSerializer, PostSerializer, CommentSerializer, ImageSerializer, APIKeySerializer, UserSerializer, FoodIntakeSerializer, RegisterSerializer


from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum

from decimal import Decimal, ROUND_HALF_UP

from rest_framework import viewsets, status, generics #added
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.authtoken.models import Token





class IsOwnerOrReadOnly(BasePermission):
    # permssion class to allow object owner to edit, and others to read.
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return obj.user == request.user

def root_view(request): #http://127.0.0.1:8000/ 에 뜨는 첫 화면 세팅인데 지워도 됨....
    return JsonResponse({"message": "Welcome to the API!"})



# apiview를 사용한 댓글 생성 api
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, post_id):
    post= get_object_or_404(Post, pk=post_id)
    serializer = CommentSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(user=request.user, post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# apiview를 사용한 api 키 생성/획득 api ____필요한가??
@api_view(['POST'])
def create_api_key_form(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST,
            )

    user = authenticate(username=username, password=password)
    if user is not None:
        api_key, created = APIKey.objects.get_or_create(user=user)
        serializer = APIKeySerializer(api_key)
        return Response(
            {'api_key': serializer.data['key']},
            status=status.HTTP_200_OK,
            )
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED,
            )





# 보드 리스트 및 세부 정보 api
class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [AllowAny]

# 게시글 리스트, 세부정보, 생성, 수정, 삭제 api
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self): # 특정 게시판의 게시글만 가져오기
        
        board_id = self.request.query_params.get('board_id')
        if board_id:
            return self.queryset.filter(board_id=board_id)
        return self.queryset
    
    def perform_create(self, serializer): # 게시글 생성 시 사용자 지정
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs): # 게시글 및 이미지 생성
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(user=request.user)

        files = request.FILES.getlist('images')
        for file in files:
            Image.objects.create(post=post, image=file)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs): # 게시글 및 이미지 수정
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

# 댓글 리스트, 생성, 수정, 삭제 api
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# 이미지 리스트, 생성, 수정, 삭제 api
class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


# apiview를 사용한 특정 게시글 및 댓글 조회 api
class PostDetailAPIView(APIView):
    permission_classes = [AllowAny]  

    def get(self, request, board_id, post_id):

        post = get_object_or_404(Post, pk=post_id)
        post_serializer = PostSerializer(post)

        comments = post.comments.all()
        comment_serializer = CommentSerializer(comments, many=True)

        # JSON 형태로 Post 및 관련 Comment 반환
        return Response(
            {
                "post": post_serializer.data,
                "comments": comment_serializer.data,
            },
        )
           












# ayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy


# Register API _________added!!!!!!!!
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": Token.objects.create(user)[1],
        })


# accounts/views.py
@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# accounts/views.py
@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        user = None
        if '@' in username:
            try:
                user = CustomUser.objects.get(email=username)
            except ObjectDoesNotExist:
                pass

        if not user:
            user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
        


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

        

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_required_intake(request):
    user = request.user
    required_intake = request.data.get('required_intake')

    if required_intake is not None:
        user.required_intake = required_intake
        user.save()
        return Response({'message': 'Required intake updated successfully.'}, status=status.HTTP_200_OK)
    
    return Response({'error': 'Required intake not provided.'}, status=status.HTTP_400_BAD_REQUEST)







class FoodIntakeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def format_decimal(self, value):
        """Decimal 값을 소수점 두 자리까지 포맷팅"""
        if value is None:
            return '0.00'
        return str(Decimal(value).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))

    def calculate_totals(self, user, date):
        """날짜를 기준으로 섭취량 총계 계산"""
        meal_totals = FoodIntake.objects.filter(
            user=user,
            date=date
        ).values('meal_time').annotate(
            total_calories=Sum('calories'),
            total_carbs=Sum('carbs'),
            total_protein=Sum('protein'),
            total_fat=Sum('fat')
        )

        daily_totals = FoodIntake.objects.filter(
            user=user,
            date=date
        ).aggregate(
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
        date = request.query_params.get('date')
        if not date:
            return Response({"detail": "Date parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not re.match(r'\d{4}-\d{2}-\d{2}', date):
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        meal_totals_dict = self.calculate_totals(request.user, date)
        return Response(meal_totals_dict, status=status.HTTP_200_OK)

    def destroy(self, request):
        deleted_count, _ = FoodIntake.objects.filter(user=request.user).delete()
        
        if deleted_count > 0:
            return Response({'message': '모든 식단 데이터가 성공적으로 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': '삭제할 데이터가 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
