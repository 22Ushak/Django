from django.db import models
from ckeditor.fields import RichTextField  # type: ignore
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


    likes = models.ManyToManyField(User, related_name='comment_like',blank=True)
    dislikes = models.ManyToManyField(User,related_name='comment_dislike',blank=True)

    def total_likes(self):
        return self.likes.count()
    
    def total_dislikes(self):
        return self.dislikes.count()


    def __str__(self):
        return f"Comment by {self.user.username} on {self.destination.name}"

    class Meta:
        ordering = ['created_at']
