from django.shortcuts import render, get_object_or_404, redirect
from .models import Destination, Comments, IPVisit
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth

def index(request):
    dests = Destination.objects.all()
    return render(request, "index.html", {'dests': dests})

def details(request, id):
    ip = get_client_ip(request)  # Get user's IP address

    # Allow logged-in users unrestricted access
    if not request.user.is_authenticated:
        # Use session to track places visited by the user
        if 'visited_places' not in request.session:
            request.session['visited_places'] = []

        visited_places = request.session['visited_places']

        # If the user has already visited 2 places, restrict further visits (including revisiting places)
        if len(visited_places) >= 2:
            # Check if this place is already visited or if it's the 3rd place
            if id in visited_places:
                return redirect('register_first')  # Redirect if visiting the same place again
            else:
                return redirect('register_first')  # Redirect if trying to visit a 3rd place

        # Add the place to the visited list if it's not already in it
        if id not in visited_places:
            visited_places.append(id)
            request.session['visited_places'] = visited_places  # Save it to the session
            request.session.modified = True  # Ensure session is saved

            # Record the visit in the database only if not already recorded for this IP and place
            if not IPVisit.objects.filter(ip_address=ip, place_id=id).exists():
                IPVisit.objects.create(ip_address=ip, place_id=id)
    
    desc = get_object_or_404(Destination, id=id)
    all_comment = Comments.objects.filter(destination=desc, parent_comment__isnull=True)
    all_replies = Comments.objects.filter(destination=desc).exclude(parent_comment__isnull=True)

    parent_comment_count = all_comment.count()
    child_comment_count = all_replies.count()

    for comment in all_comment:
        comment.child_count = all_replies.filter(parent_comment=comment).count()

    if request.method == "POST":
        comment_text = request.POST.get('comment', '').strip()
        parent_comment_id = request.POST.get('parent_comment')

        if request.user.is_authenticated and comment_text:
            if parent_comment_id:
                parent_comment = Comments.objects.get(id=parent_comment_id)
                Comments.objects.create(comment=comment_text, user=request.user, destination=desc, parent_comment=parent_comment)
            else:
                Comments.objects.create(comment=comment_text, user=request.user, destination=desc)
            return redirect('details', id=id)

    return render(request, 'details.html', {
        'desc': desc,
        'comments': all_comment,
        'replies': all_replies,
        'parent_comment_count': parent_comment_count,
        'child_comment_count': child_comment_count,
    })

def register_first(request):
    return render(request, 'register_first.html')

@login_required
def like_dislike_comment(request, comment_id, action):
    comment = get_object_or_404(Comments, id=comment_id)

    if action == "like":
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
        else:
            comment.likes.add(request.user)
            comment.dislikes.remove(request.user)

    elif action == "dislike":
        if request.user in comment.dislikes.all():
            comment.dislikes.remove(request.user)
        else:
            comment.dislikes.add(request.user)
            comment.likes.remove(request.user)

    return redirect(request.META.get("HTTP_REFERER", "details"))

def get_client_ip(request):
    """Retrieve the real IP address of the user."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
