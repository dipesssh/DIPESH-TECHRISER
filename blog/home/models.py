from django.db import models
import uuid
from django.contrib.auth.models import User


# Base model to reuse common fields

class BaseModel(models.Model):
    uid= models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)

    class Meta:
        abstract = True

# Blog model for storing blog posts

class Blog(BaseModel):
    user = models.ForeignKey( User, on_delete=models.CASCADE, related_name="blogs")
    title = models.CharField(max_length=500)
    blog_text = models.TextField()
    main_image = models.ImageField(upload_to="blogs")

    def __str__(self) -> str:
        return self.title



class Comment(BaseModel):
    """
    Model for storing user comments on blog posts.
    """
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="The blog post this comment belongs to"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="The user who wrote this comment"
    )
    text = models.TextField(
        max_length=1000,
        help_text="The comment content (max 1000 chars)"
    )

    class Meta:
        ordering = ['-created_at']  # Newest comments first

    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog.title}"
