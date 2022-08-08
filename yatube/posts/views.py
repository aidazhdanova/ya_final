from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CommentForm, PostForm
from .models import Post, Group, Follow, User
from django.views.decorators.cache import cache_page


def paginator_func(posts, request):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(60 * 20)
def index(request):
    post_list = Post.objects.select_related('author', 'group').all()
    page_obj = paginator_func(post_list, request)
    return render(request, 'posts/index.html', {'page_obj': page_obj})


def group_posts(request, slug):
    """Возращаем 10 постов"""
    group = get_object_or_404(Group, slug=slug)
    all_post = group.posts.all()
    page_obj = paginator_func(all_post, request)

    return render(
        request,
        'posts/group_list.html',
        {'page_obj': page_obj, 'group': group})


def profile(request, username):
    """Показываем профиль пользователя"""
    author = get_object_or_404(User, username=username)
    posts_all = author.posts.all()
    page_obj = paginator_func(posts_all, request)
    following = (request.user.is_authenticated and author != request.user
                 and Follow.objects.filter(user=request.user,
                                           author=author).exists())
    return render(request, 'posts/profile.html', {
        'page_obj': page_obj,
        'author': author,
        'following': following,
    })


def post_detail(request, post_id):
    """Показываем пост"""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.select_related('author')
    form = CommentForm()
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })


@login_required
def post_create(request):
    """Создаём новый пост"""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)
    return render(request, 'posts/create_post.html', {
        'form': form
    })


@login_required
def post_edit(request, post_id):
    """Редактируем пост."""
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/create_post.html', {
        'post': post,
        'form': form,
        'is_edit': True,
    })


@login_required
def add_comment(request, post_id):
    """Комментарии."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator_func(post_list, request)
    return render(request, 'posts/follow.html', {'page_obj': page_obj})


@login_required
def profile_follow(request, username):
    """Подписки."""
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(author=author, user=request.user)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    """Отписка."""
    get_object_or_404(Follow, user=request.user,
                      author__username=username).delete()
    return redirect('posts:profile', username=username)
