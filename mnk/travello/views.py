from django.shortcuts import render, get_object_or_404, redirect
from .models import Destination, Comments, IPVisit,CustomUser
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User, auth
from .forms import UploadCSVForm
import csv
from django.http import HttpResponse
from .forms import UploadCSVForm
from .models import User
from datetime import datetime
# import io
# from django.core.exceptions import ValidationError
# from .models import User
# from django.core.files.storage import FileSystemStorage


def index(request):
    dests = Destination.objects.all()
    return render(request, "index.html", {'dests': dests})

def details(request, id):
    ip = get_client_ip(request)  # Get user's IP address

    if not request.user.is_authenticated:
        
        if 'visited_places' not in request.session:# Use session to track places visited by the user
            request.session['visited_places'] = []

        visited_places = request.session['visited_places']

        if len(visited_places) >= 2:
            # Check if this place is already visited or if it's the 3rd place
            if id in visited_places:
                return redirect('register_first')  
            else:
                return redirect('register_first')  

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


from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import UploadCSVForm
from .models import CustomUser  # Assuming this is your model to store user data
import csv
import psycopg2
from psycopg2 import extras
from django.core.files.storage import FileSystemStorage
import io

# Function to insert data into the database in batches
def insert_data_to_db(cursor, rows):
    insert_query = '''
        INSERT INTO CustomUser (id, name, email, address, status, created_at, updated_at)
        VALUES %s
        ON CONFLICT (email) DO NOTHING  -- Prevent duplicate email insertions
    '''
    extras.execute_values(cursor, insert_query, rows)
    cursor.connection.commit() 
def insert_data_in_chunks(file, chunk_size=100):
    conn = psycopg2.connect(
        host='localhost',
        dbname='user_data',
        user='postgres',   
        password='1234', 
    )
    cursor = conn.cursor()

   
    file.seek(0) 
    reader = csv.reader(io.StringIO(file.read().decode('utf-8')))
    header = next(reader) 
    
    rows = []
    for row in reader:
        if len(row) != 7:  
            continue 

        try:
            id, name, email, address, status, created_at, updated_at = row
            created_at = created_at.strip() 
            updated_at = updated_at.strip()

            rows.append((
                int(id),
                name,
                email,
                address,
                status,
                created_at,
                updated_at
            ))

        except ValueError:
            continue

        if len(rows) >= chunk_size:
            insert_data_to_db(cursor, rows)
            rows = []  
    if rows:
        insert_data_to_db(cursor, rows)
    
    cursor.close()
    conn.close()

@login_required
def upload_csv(request):
    """
    This view handles the CSV file upload, processes the file, and inserts its data into the database.
    """
    if request.method == 'POST' and request.FILES.get('csv_file'):
        form = UploadCSVForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = request.FILES['csv_file']

            try:
                insert_data_in_chunks(csv_file, chunk_size=100)
                return HttpResponse('CSV file has been successfully uploaded and data has been inserted into the database.')

            except Exception as e:
                return HttpResponse(f"An error occurred while processing the CSV file: {e}")
    else:
        form = UploadCSVForm()

    return render(request, 'upload_csv.html', {'form': form})



