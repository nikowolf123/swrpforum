from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

from .models import Topic, Post, Tag, UserModeration
from .forms import TopicForm, PostForm, ManageAccountForm

def topic_list(request):
    all_tags = Tag.objects.all().order_by('name')
    pinned_topics = Topic.objects.filter(pinned=True).order_by('-created_at')
    other_topics = Topic.objects.filter(pinned=False).order_by('-created_at')
    context = {
        'pinned_topics': pinned_topics,
        'other_topics': other_topics,
        'all_tags': all_tags
    }
    return render(request, 'forum/topic_list.html', context)

def filter_topics(request):
    tag_ids = request.GET.getlist('tags[]', [])
    if tag_ids:
        topics = Topic.objects.filter(tags__in=tag_ids).distinct().order_by('-created_at')
    else:
        topics = Topic.objects.all().order_by('-created_at')
    pinned = topics.filter(pinned=True)
    non_pinned = topics.filter(pinned=False)
    data = {
        'pinned_topics': [
            {
                'id': t.id,
                'title': t.title,
                'content': t.content[:150],
                'author': t.author.username,
                'pinned': t.pinned
            } for t in pinned
        ],
        'other_topics': [
            {
                'id': t.id,
                'title': t.title,
                'content': t.content[:150],
                'author': t.author.username,
                'pinned': t.pinned
            } for t in non_pinned
        ]
    }
    return JsonResponse(data)

def topic_detail(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    posts = topic.posts.all().order_by('created_at')
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.topic = topic
                post.save()
                return redirect('topic_detail', pk=topic.pk)
        else:
            return redirect('login')
    else:
        form = PostForm()
    context = {
        'topic': topic,
        'posts': posts,
        'form': form,
    }
    return render(request, 'forum/topic_detail.html', context)

@login_required
def create_topic(request):
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            topic.save()
            form.save_m2m()
            return redirect('topic_detail', pk=topic.pk)
    else:
        form = TopicForm()
    return render(request, 'forum/create_topic.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)
def edit_topic(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    if request.method == 'POST':
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            return redirect('topic_detail', pk=topic.id)
    else:
        form = TopicForm(instance=topic)
    return render(request, 'forum/edit_topic.html', {'form': form, 'topic': topic})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('topic_list')
    else:
        form = UserCreationForm()
    return render(request, 'forum/signup.html', {'form': form})

@login_required
def manage_account(request):
    if request.method == 'POST':
        form = ManageAccountForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('manage_account')
    else:
        form = ManageAccountForm(instance=request.user)
    return render(request, 'forum/manage_account.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    total_topics = Topic.objects.count()
    total_posts = Post.objects.count()
    total_users = User.objects.count()
    latest_topics = Topic.objects.order_by('-created_at')[:5]
    latest_posts = Post.objects.order_by('-created_at')[:5]
    recent_users = User.objects.order_by('-date_joined')[:5]
    top_active_users = User.objects.annotate(num_posts=Count('post')).order_by('-num_posts')[:5]
    context = {
        'total_topics': total_topics,
        'total_posts': total_posts,
        'total_users': total_users,
        'latest_topics': latest_topics,
        'latest_posts': latest_posts,
        'recent_users': recent_users,
        'top_active_users': top_active_users,
    }
    return render(request, 'forum/admin_dashboard.html', context)

@user_passes_test(lambda u: u.is_staff)
def manage_tags(request):
    if request.method == 'POST':
        tag_name = request.POST.get('name')
        if tag_name:
            from django.utils.text import slugify
            slug = slugify(tag_name)
            Tag.objects.get_or_create(name=tag_name, slug=slug)
    tags = Tag.objects.all().order_by('name')
    return render(request, 'forum/manage_tags.html', {'tags': tags})

@user_passes_test(lambda u: u.is_staff)
def user_lookup(request):
    query = request.GET.get('q', '')
    users = []
    if query:
        users = User.objects.filter(username__icontains=query)
    return render(request, 'forum/user_lookup.html', {'query': query, 'users': users})

@user_passes_test(lambda u: u.is_staff)
def user_detail(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    posts = Post.objects.filter(author=user_obj).order_by('-created_at')
    moderation, created = UserModeration.objects.get_or_create(user=user_obj)
    return render(request, 'forum/user_detail.html', {
        'user_obj': user_obj,
        'posts': posts,
        'moderation': moderation,
        'now': timezone.now()
    })

@user_passes_test(lambda u: u.is_staff)
@require_POST
def user_action(request, user_id, action):
    user_obj = get_object_or_404(User, id=user_id)
    moderation, created = UserModeration.objects.get_or_create(user=user_obj)
    if action == 'ban':
        user_obj.is_active = False
        user_obj.save()
        moderation.banned = True
    elif action == 'unban':
        user_obj.is_active = True
        user_obj.save()
        moderation.banned = False
    elif action == 'timeout':
        moderation.timeout_until = timezone.now() + timedelta(minutes=15)
    elif action == 'remove_timeout':
        moderation.timeout_until = None
    moderation.save()
    return redirect('user_detail', user_id=user_id)

@user_passes_test(lambda u: u.is_staff)
@require_POST
def set_timeout(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    moderation, created = UserModeration.objects.get_or_create(user=user_obj)
    try:
        minutes = int(request.POST.get('timeout_minutes', 0))
    except ValueError:
        minutes = 0
    if minutes > 0:
        moderation.timeout_until = timezone.now() + timedelta(minutes=minutes)
    else:
        moderation.timeout_until = None
    moderation.save()
    return redirect('user_detail', user_id=user_id)

@user_passes_test(lambda u: u.is_staff)
@require_POST
def toggle_pin_topic(request, topic_id, action):
    topic = get_object_or_404(Topic, id=topic_id)
    if action == 'pin':
        topic.pinned = True
        topic.save()
        return redirect('topic_list')
    elif action == 'unpin':
        topic.pinned = False
        topic.save()
        return redirect('topic_list')
