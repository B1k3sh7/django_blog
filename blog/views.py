from django.shortcuts import render, get_object_or_404, redirect
from blog.models import Post, Comment
from blog.forms import InputForm, PostForm, CommentForm
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (TemplateView, ListView,
                                    DetailView, CreateView,
                                    UpdateView, DeleteView)

from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect

# Create your views here.

class AboutView(TemplateView):
    template_name = 'about.html'


class PostListView(ListView):
    model = Post

    def get_queryset(self):
        #lte=less than or equalto
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    

class PostDetailView(DetailView):
    model = Post


class CreatePostView(LoginRequiredMixin, CreateView):
    login_url = '/login'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm 

    model = Post


class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm 

    model = Post


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('post_list')


class DraftListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    redirect_field_name = 'blog/post_list.html'
    model = Post


    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('created_date')
    


######################
@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()  #.publish() function comes from class Post of models.py
    return redirect('post_detail', pk=pk)


def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post  #.post come from models.py of class Comment
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/comment_form.html', {'form':form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    #.approve() function come from models.py of class Comment
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request,pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)



@csrf_protect
def user_login(request):
    if request.method == "POST":
        form = InputForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            username = request.POST['username']
            password = request.POST['password']
            user =  authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return render(request, 'blog/post_list.html')
        else:
            form = InputForm()
            return render(request, 'registration/login.html', {'form': form})
    else:
        return render(request, 'registration/login.html', {'error_message': 'Incorrect username and/or password.'})

    
def user_logout(request):
    logout(request)
