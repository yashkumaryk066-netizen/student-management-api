from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.text import slugify

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True, allow_unicode=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    content = models.TextField()
    excerpt = models.TextField(blank=True, help_text="Short summary for SEO and listing")
    published_date = models.DateTimeField(default=timezone.now)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    # SEO Fields
    meta_title = models.CharField(max_length=250, blank=True, help_text="SEO title tag")
    meta_description = models.TextField(blank=True, help_text="SEO meta description")
    meta_keywords = models.CharField(max_length=500, blank=True, help_text="SEO meta keywords")
    featured_image = models.ImageField(upload_to='blog/%Y/%m/%d/', blank=True, null=True)

    class Meta:
        ordering = ('-published_date',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog:post_detail', args=[self.slug])
