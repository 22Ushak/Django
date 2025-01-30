# from django.shortcuts import render, get_object_or_404, redirect
# from .models import Destination, Comments
# from django.contrib.auth.decorators import login_required

# def index(request):
#     dests = Destination.objects.all()
#     return render(request, "index.html", {'dests': dests})

# def details(request, id):
#     desc = get_object_or_404(Destination, id=id)
#     all_comment = Comments.objects.filter(destination=desc, parent_comment__isnull=True)  # Only top-level comments
#     all_replies = Comments.objects.filter(destination=desc).exclude(parent_comment__isnull=True)  # All replies

#     parent_comment_count=all_comment.count()
#     child_comment_count=all_replies.count()
#     for comment in all_comment:
#         comment.child_count = all_replies.filter(parent_comment=comment).count()


#     if request.method == "POST":
#         comment_text = request.POST.get('comment', '').strip() #stores comment enterd by user
#         parent_comment_id = request.POST.get('parent_comment')  # To check if it's a reply

#         if request.user.is_authenticated and comment_text:
#             if parent_comment_id:
#                 parent_comment = Comments.objects.get(id=parent_comment_id)  # Get the parent comment
#                 Comments.objects.create(comment=comment_text, user=request.user, destination=desc, parent_comment=parent_comment) #saves the new comment as reply
#             else:
#                 Comments.objects.create(comment=comment_text, user=request.user, destination=desc)
#             return redirect('details', id=id)  # Refresh page to show new comment or reply

#     return render(request, 'details.html', {
#         'desc': desc,
#         'comments': all_comment,
#         'replies': all_replies,
#         'parent_comment_count': parent_comment_count,
#         'child_comment_count': child_comment_count,
#     })


from django.shortcuts import render, get_object_or_404, redirect
from .models import Destination, Comments
from django.contrib.auth.decorators import login_required

def index(request):
    dests = Destination.objects.all()
    return render(request, "index.html", {'dests': dests})

def details(request, id):
    desc = get_object_or_404(Destination, id=id)
    all_comment = Comments.objects.filter(destination=desc, parent_comment__isnull=True)  # Only top-level comments
    all_replies = Comments.objects.filter(destination=desc).exclude(parent_comment__isnull=True)  # All replies

    parent_comment_count=all_comment.count()
    child_comment_count=all_replies.count()
    for comment in all_comment:
        comment.child_count = all_replies.filter(parent_comment=comment).count()


    if request.method == "POST":
        comment_text = request.POST.get('comment', '').strip() #stores comment enterd by user
        parent_comment_id = request.POST.get('parent_comment')  # To check if it's a reply

        if request.user.is_authenticated and comment_text:
            if parent_comment_id:
                parent_comment = Comments.objects.get(id=parent_comment_id)  # Get the parent comment
                Comments.objects.create(comment=comment_text, user=request.user, destination=desc, parent_comment=parent_comment) #saves the new comment as reply
            else:
                Comments.objects.create(comment=comment_text, user=request.user, destination=desc)
            return redirect('details', id=id)  # Refresh page to show new comment or reply




    return render(request, 'details.html', {
        'desc': desc,
        'comments': all_comment,
        'replies': all_replies,
        'parent_comment_count': parent_comment_count,
        'child_comment_count': child_comment_count,
    })

@login_required
def like_dislike_comment(request, comment_id, action):
    comment = get_object_or_404(Comments, id=comment_id)

    if action == "like":
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)  # Unlike
        else:
            comment.likes.add(request.user)  # Like
            comment.dislikes.remove(request.user)  # Remove dislike if present

    elif action == "dislike":
        if request.user in comment.dislikes.all():
            comment.dislikes.remove(request.user)  # Remove dislike
        else:
            comment.dislikes.add(request.user)  # Dislike
            comment.likes.remove(request.user)  # Remove like if present

    return redirect(request.META.get("HTTP_REFERER", "details")) 