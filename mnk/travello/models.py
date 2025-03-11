from django.db import models
from ckeditor.fields import RichTextField  
from django.contrib.auth.models import User

class Destination(models.Model):
    name = models.CharField(max_length=100)
    img = models.ImageField()
    desc = RichTextField()
    price = models.IntegerField()
    offer = models.BooleanField(default=False)

class Comments(models.Model):
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    likes = models.ManyToManyField(User, related_name='comment_like', blank=True)
    dislikes = models.ManyToManyField(User, related_name='comment_dislike', blank=True)

    def total_likes(self):
        return self.likes.count()
    
    def total_dislikes(self):
        return self.dislikes.count()

    def __str__(self):
        return f"Comment by {self.user.username} on {self.destination.name}"

    class Meta:
        ordering = ['created_at']

class IPVisit(models.Model):
    ip_address = models.CharField(max_length=255)
    place_id = models.CharField(max_length=255)  # stores the visited place id
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} visited {self.place_id}"

class CustomUser(models.Model):  # Renamed to avoid conflict with the built-in User model
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    address = models.TextField()
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Suspended', 'Suspended'), ('Inactive', 'Inactive')])
    created_at = models.DateField()
    updated_at = models.DateField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'customuser'  # Explicitly set the table name if needed.

class CSVUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CSV File uploaded at {self.uploaded_at}"
