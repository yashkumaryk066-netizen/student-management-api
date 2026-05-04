from django.test import TestCase, Client
from blog.models import Post
from django.urls import reverse
from django.contrib.auth.models import User

class BlogAndSEOTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='blogger', password='password123')
        self.post = Post.objects.create(
            title="A to Z ERP Guide",
            slug="a-to-z-erp-guide",
            content="Full details about ERP features.",
            status='published',
            author=self.user,
            meta_title="Premium ERP Guide",
            meta_description="Everything you need to know about Y.S.M ERP"
        )

    def test_blog_listing(self):
        """Test that published blog posts appear in the list"""
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A to Z ERP Guide")

    def test_blog_detail(self):
        """Test blog detail view and SEO meta tags"""
        response = self.client.get(reverse('blog:post_detail', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Premium ERP Guide")
        self.assertContains(response, "Everything you need to know about Y.S.M ERP")

    def test_robots_txt(self):
        """Test robots.txt accessibility and content"""
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertIn('User-agent: *', response.content.decode())
        self.assertIn('Disallow: /admin/', response.content.decode())

    def test_sitemap_xml(self):
        """Test sitemap.xml accessibility and content"""
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<loc>', response.content.decode())
        self.assertIn('a-to-z-erp-guide', response.content.decode())
