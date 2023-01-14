from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView
from .forms import EmailPostForm
from .models import Post
from django.core.mail import send_mail
from .forms import CommentsForm
from taggit.models import Tag
# pagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3) # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    tag =None 
    
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = object_list.filter(tags__in=[tag])
    

    return render(request,
    'blog/post/list.html',
    {'posts': posts,"tag":tag, 'page': page})

# class PostListView(ListView):
#         queryset = Post.published.all()
#         context_object_name = 'posts'
#         paginate_by = 3
#         template_name = 'blog/post/list.html'   
def post_detail(request, year, month, day, post):
        post = get_object_or_404(Post, slug=post,
            status='published',
            publish__year=year,
            publish__month=month,
            publish__day=day)
        comments = post.comments.filter(active=True)
        new_comment = None
        if request.method =='POST':
    #   <----------------A comment post was creates--------------->
            comment_form =CommentsForm (data=request.POST)   
            if comment_form.is_valid():
    #   <----------------Create comment- object but donot  save to the database yet-------------->
                new_comment = comment_form.save(commit=False)
    #   <----------------Assign the current post to the comment--------------->
                new_comment.post = post
                # Save the comment to the database
                new_comment.save()
        else:
             comment_form = CommentsForm()
        
        # list of similar posts
        post_tags_ids = post.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
        similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
        print(similar_posts)
        return render(request,'blog/post/detail.html',{'post': post,
                                                       'similar_posts': similar_posts,
                                                       'comment_form':comment_form,
                                                       'comments':comments})
        
       
# def post_share(request,  post_id):
#     # Retrieve post by id
#     post = get_object_or_404(Post, id=post_id, status='published')
    
#     if request.method=='POST':
#         # Form was submmitted
#         form = EmailPostForm(request.POST)
#         if form.is_valid():
#             # Form field passed validation
#             cd = form.cleaned_data
#             #... send email to
#     else:
#         form = EmailPostForm()
#     return render(request, 'blog/post/share.html',{'post':post, 'form':form})





def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent =False
    if request.method=='POST':
        # Form was submmitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form field passed validation
            cd = form.cleaned_data
            #... send email to
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you to read {post.title}"
            message = f"Read{post.title} at {post_url} \n {cd['name']}\'s comments:{cd['comments']}" 
            send_mail(subject, message, 'mukiibijosephgilbert865@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html',{'post':post, 
                                                   'form':form,
                                                   'sent':sent})



