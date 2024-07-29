from django.shortcuts import render, get_object_or_404, redirect
from .models import Board, Post, Comment, Image, APIKey 
from .forms import PostForm, CommentForm, ImageForm
from .serializers import BoardSerializer, PostSerializer, CommentSerializer, ImageSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, status, serializers   # serializers,  permissions, views
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, action
from rest_framework.permissions import AllowAny

# api key
@api_view(['POST'])
def create_api_key(request):
    # 인증없이 접근 가능
    username = request.data.get('username')
    password = request.data.get('password')

    # 사용자 인증 처리
    user = authenticate(username=username, password=password)
    if user is not None:
        api_key, created = APIKey.objects.get_or_create(user=user)
        return Response({'api_key': str(api_key.key)}, status=status.HTTP_201_CREATED)
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)




# DRF ViewSets
class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [AllowAny]  # 인증 필요없음

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        seriaizer = self.get_serializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        post = serializers.save()

        # handle mltiple file uploads
        files = request.FILES.getlist('images')
        for file in files:
            Image.objects.create(post=post, image=file)

        headers = self.get_success_headers(serializers.data)
        return Response(serializers.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()

        # Handle multiple file uploads
        files = request.FILES.getlist('images')
        for file in files:
            Image.objects.create(post=post, image=file)

        # Handle image deletions
        image_ids_to_delete = request.data.get('delete_images', [])
        for image_id in image_ids_to_delete:
            Image.objects.filter(id=image_id).delete()

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)



class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [AllowAny]

    




# Django 템플릿 뷰

def index(request):
    boards = Board.objects.all()
    return render(request, 'practice/index.html', {'boards': boards})

def board_detail(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    posts = board.post_set.all()

    # Pagination
    page = request.GET.get('page',1)
    paginator = Paginator(posts, 10)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'practice/board_detail.html', { 
        'board': board,
        'posts': posts,
        })



def post_detail(request, board_id, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', board_id=board_id, post_id=post_id)
    else:
        form = CommentForm()
    return render(request, 'practice/post_detail.html', {'post': post, 'comments': comments, 'form': form})

# @login_required(login_url='user/login') # 서연언니 로그인 url 참고
def new_post(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        image_formset = ImageFormSet(request.POST, request.FILES, queryset=Image.objects.none())
        if form.is_valid() and image_formset.is_valid():
            post = form.save()
            images = image_formset.save(commit=False)
            for image in images : 
                image.post = post
                image.save()


            post.board = board
            post.save()

            # Handle multiple file uploads
            files = request.FILES.getlist('images')
            for file in files:
                Image.objects.create(post=post, image=file)

            return redirect('post_detail', board_id=board_id, post_id=post.id)
    else:
        form = PostForm()
    return render(request, 'practice/new_post.html', {'form': form, 'board': board})


def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    board = post.board

    if request.method == "POST":
        post_form = PostForm(request.POST, instance=post)
        if post_form.is_valid():
            post = post_form.save() # 일단 저장

            # Handle multiple file uploads
            files = request.FILES.getlist('images')
            for file in files:
                Image.objects.create(post=post, image=file)

            # Handle image deletions
            image_ids_to_delete = request.POST.getlist('delete_images')
            for image_id in image_ids_to_delete:
                Image.objects.filter(id=image_id).delete()

            return redirect('post_detail', board_id=post.board_id, post_id=post.id)
    else:
        post_form = PostForm(instance=post)

    images = post.images.all()  # Fetch all images related to the post

    return render(request, 'practice/edit_post.html', {
        'post_form': post_form, 
        'images': images,
        'board': board,
    })

def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    board_id = post.board_id
    post.delete()
    return redirect('board_detail', board_id=board_id)




"""
# 사용자 등록 Serializer
class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)
    password2 = serializers.CharField(max_length=100)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
"""


"""
# 사용자 등록 View
class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=201)
        return Response(serializer.errors, status=400)
"""