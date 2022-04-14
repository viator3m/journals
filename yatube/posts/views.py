from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.urls import reverse

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow

NUMBER_OF_POSTS = 10


def paginate(request, element):
    paginator = Paginator(element, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    page_obj = paginate(request, posts)
    groups = Group.objects.all()
    context = {
        'posts': posts,
        'groups': groups,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginate(request, posts)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = paginate(request, posts)
    template = 'posts/profile.html'

    user = request.user
    following = False
    if user.is_authenticated:
        following = Follow.objects.filter(
            user=user,
            author=author
        ).exists()

    context = {
        'posts': posts,
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    is_edit = post.author == request.user
    template = 'posts/post_detail.html'
    form = CommentForm()
    comments = post.comment.all()
    context = {
        'post': post,
        'is_edit': is_edit,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        url = reverse('posts:profile', args=(request.user,))
        return redirect(url)
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    is_edit = post.author == request.user
    form = PostForm(
        request.POST or None,
        instance=post,
        files=request.FILES or None
    )
    if not post.author == request.user:
        return redirect('posts:post_detail', post.pk)

    if request.method == 'POST' and form.is_valid():
        form.save()
        url = reverse('posts:post_detail', args=(post.id,))
        return redirect(url)

    context = {
        'post': post,
        'is_edit': is_edit,
        'form': form,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    url = 'posts:post_detail'
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, pk=post_id)
        comment.save()
    return redirect(url, post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginate(request, posts)
    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj,
    }
    if not posts:
        context['empty'] = True
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    url = reverse('posts:profile', args=(username,))

    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)

    return redirect(url)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    url = reverse('posts:profile', args=(username,))
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect(url)
