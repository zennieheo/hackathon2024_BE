from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
import uuid
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework_simplejwt.tokens import RefreshToken


from .models import Board, Post, Comment, Image, APIKey
from .forms import PostForm, CommentForm, ImageForm  
from .serializers import BoardSerializer, PostSerializer, CommentSerializer, ImageSerializer, APIKeySerializer


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'message': 'This is a protected view!'})

# Custom permission class
class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return obj.user == request.user

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, post_id):
    post= get_object_or_404(Post, pk=post_id)
    serializer = CommentSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(user=request.user, post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_api_key_form(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user is not None:
        api_key, created = APIKey.objects.get_or_create(user=user)
        serializer = APIKeySerializer(api_key)
        return Response({'api_key': serializer.data['key']}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)





# DRF ViewSets
class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [AllowAny]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(user=request.user)

        files = request.FILES.getlist('images')
        for file in files:
            Image.objects.create(post=post, image=file)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
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
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


# Django Template Views
def index(request):
    boards = Board.objects.all()
    return render(request, 'practice/index.html', {'boards': boards})


def board_detail(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    posts = board.post_set.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(posts, 10)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'practice/board_detail.html', {'board': board, 'posts': posts})


def post_detail(request, board_id, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('post_detail', board_id=board_id, post_id=post_id)
    else:
        form = CommentForm()

    return render(request, 'practice/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        })





@login_required
def new_post(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        image_form = ImageForm(request.POST, request.FILES, instance=board )  # queryset=Image.objects.none()
        if form.is_valid() and image_form.is_valid():
            post = form.save(commit=False)
            post.board = board
            post.user = request.user
            post.save()

            image_form.instance = post
            image_form.save()

            """
            files = request.FILES.getlist('images')
            for file in files:
                Image.objects.create(post=post, image=file)

            """
            
            return redirect('post_detail', board_id=board_id, post_id=post.id)
    else:
        form = PostForm()
        image_form = ImageForm(instance=board)

    return render(request, 'practice/new_post.html', {'form': form, 'board': board})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    board = post.board

    if not request.user.is_authenticated:
        return redirect('login')

    if post.user != request.user:
        return redirect('post_detail', board_id=post.board.id, post_id=post.id)

    if request.method == "POST":
        post_form = PostForm(request.POST, instance=post)
        if post_form.is_valid():
            post = post_form.save()

            files = request.FILES.getlist('images')
            for file in files:
                Image.objects.create(post=post, image=file)

            image_ids_to_delete = request.POST.getlist('delete_images')
            for image_id in image_ids_to_delete:
                Image.objects.filter(id=image_id).delete()

            return redirect('post_detail', board_id=post.board_id, post_id=post.id)
    else:
        post_form = PostForm(instance=post)

    images = post.images.all()
    return render(request, 'practice/edit_post.html', {'post_form': post_form, 'images': images, 'board': board})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.user != request.user:
        return redirect('post_detail', board_id=post.board.id, post_id=post.id)

    board_id = post.board_id
    post.delete()
    return redirect('board_detail', board_id=board_id)

