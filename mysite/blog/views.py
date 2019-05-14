from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import (TemplateView,ListView,
                            DetailView,CreateView,UpdateView,DeleteView)
from .models import Post,Profile,Comment
from django.utils import timezone
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your views here.
def post_list(request):
    post_list = Post.published.all().order_by('-id')
    query = request.GET.get('q')
    if query:
        post_list = Post.published.filter(
        Q(title__icontains=query)|
        Q(author__username=query)|
        Q(body__icontains=query)
        )
    paginator = Paginator(post_list, 5)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    if page is None:
        start_index = 0
        end_index = 7
    else:
        (start_index, end_index) = proper_pagination(posts, index=3)

    page_range = list(paginator.page_range)[start_index:end_index]

    context = {
        'posts': posts,
        'page_range': page_range,
    }
    return render(request,'blog/post_list.html',context)


def proper_pagination(posts, index):
    start_index = 0
    end_index = 7
    if posts.number > index:
        start_index = posts.number - index
        end_index = start_index + end_index
    return (start_index, end_index)


# def post_detail(request, id, slug):
#     post = get_object_or_404(Post, id=id, slug=slug)
#     comments = Comment.objects.filter(post=post).order_by('-id')
#     is_liked = False
#     if post.likes.filter(id=request.user.id).exists():
#         is_liked = True
#
#     if request.method == 'POST':
#         comment_form = CommentForm(request.POST or None)
#         if comment_form.is_valid():
#             content = request.POST.get('content')
#             comment = Comment.objects.create(post=post, user=request.user, content=content)
#             comment.save()
#             return HttpResponseRedirect(post.get_absolute_url())
#     else:
#         comment_form= CommentForm()
#
#     context = {
#         'post': post,
#         'is_liked': is_liked,
#         'total_likes': post.total_likes(),
#         'comments':comments,
#         'comment_form': comment_form,
#
#     }
#     return render(request, 'blog/post_detail.html', context)

def post_detail(request, id, slug):
    post = get_object_or_404(Post, id=id, slug=slug)
    comments = Comment.objects.filter(post=post, reply=None).order_by('-id')
    is_liked = False
    is_favourite = False
    if post.likes.filter(id=request.user.id).exists():
        is_liked = True

    if post.favourite.filter(id=request.user.id).exists():
        is_favourite = True

    if request.method == 'POST':
        comment_form = CommentForm(request.POST or None)
        if comment_form.is_valid():
            content = request.POST.get('content')
            reply_id = request.POST.get('comment_id')
            comment_qs = None
            if reply_id:
                comment_qs = Comment.objects.get(id=reply_id)
            comment = Comment.objects.create(post=post, user=request.user, content=content, reply=comment_qs)
            comment.save()
            # return HttpResponseRedirect(post.get_absolute_url())
    else:
        comment_form= CommentForm()

    context = {
        'post': post,
        'is_liked': is_liked,
        'is_favourite': is_favourite,
        'total_likes': post.total_likes(),
        'comments': comments,
        'comment_form': comment_form,
    }
    if request.is_ajax():
        html = render_to_string('blog/comments.html', context, request=request)
        return JsonResponse({'form': html})

    return render(request, 'blog/post_detail.html', context)


def post_favourite_list(request):
    user = request.user
    favourite_posts = user.favourite.all()
    context = {
        'favourite_posts': favourite_posts,
    }
    return render(request, 'blog/post_favourite_list.html', context)

def favourite_post(request, id):
    post = get_object_or_404(Post, id=id)
    if post.favourite.filter(id=request.user.id).exists():
        post.favourite.remove(request.user)
    else:
        post.favourite.add(request.user)
    return HttpResponseRedirect(post.get_absolute_url())


def like_post(request):
    # post = get_object_or_404(Post, id=request.POST.get('post_id'))
    post = get_object_or_404(Post, id=request.POST.get('id'))
    is_liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True
    context = {
        'post': post,
        'is_liked': is_liked,
        'total_likes': post.total_likes(),
    }
    if request.is_ajax():
        html = render_to_string('blog/like_section.html', context, request=request)
        return JsonResponse({'form': html})


def post_edit(request, id):
    post = get_object_or_404(Post,id=id)
    if post.author != request.user:
        raise Http404()
    if request.method == "POST":
        form = PostEditForm(request.POST or None, instance=post)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(post.get_absolute_url())
    else:
        form = PostEditForm(instance=post)
    context = {
    'form': form,
    'post': post,
    }
    return render(request,'blog/post_edit.html', context)




def post_create(request):
    if request.method == 'POST':
        form = PostCreateForm(request.POST)
        #formset = ImageFormset(request.POST or None, request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
        return redirect('post_list')
    else:
        form=PostCreateForm()

    context={
    'form':form
    }
    messages.success(request, "Post has been successfully created.")
    return render(request,'blog/post_create.html',context)

# from django.views.generic.edit import UpdateView
#
#
# class PostUpdateView(UpdateView):
#     template_name='blog/post_edit.html'
#     redirect_field_name='blog/post_detail'
#     form_class=PostEditForm
#     model=Post
#


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('post_list'))
                else:
                    return HttpResponse("User is not active")
            else:
                return HttpResponse("User is None")
    else:
        form = UserLoginForm()

    context = {
        'form': form,
    }
    return render(request,'blog/login.html',context)


def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    if request.user != post.author:
        raise Http404()
    post.delete()
    messages.warning(request, 'post has been successfully deleted!')
    return redirect('post_list')



def user_logout(request):
    logout(request)
    return redirect('post_list')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            return HttpResponseRedirect(reverse('post_list'))
    else:
        form = UserRegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'registration/register.html', context)



@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(data=request.POST or None, instance=request.user)
        profile_form = ProfileEditForm(data=request.POST or None, instance=request.user.profile, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            print(profile_form)
            user_form.save()
            profile_form.save()
            return HttpResponseRedirect(reverse("post_list"))
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request,'blog/edit_profile.html',context)
