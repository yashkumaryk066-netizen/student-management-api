from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.http import HttpResponse

def post_list(request):
    try:
        object_list = Post.objects.filter(status='published')
        paginator = Paginator(object_list, 9) # 9 posts per page
        page = request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        
        return render(request, 'blog/list.html', {'posts': posts, 'page': page})
    except Exception as e:
        return HttpResponse(f"Error in Blog: {str(e)}", status=500)

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    return render(request, 'blog/detail.html', {'post': post})
