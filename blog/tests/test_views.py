from django.test import TestCase, Client
from django.contrib.auth.models import User
from blog.models import Post
from django.urls import reverse
from django.utils import timezone
from django.contrib.messages import get_messages

unquoted_content = "Test content <p>```with a block quote```</p> end content"
quoted_content = 'Test content<p style="display:flex; justify-content:center; align-items:center; font-style:italic">with a block quote</p> end content'


def post_no_quotes():
    post = Post.objects.create(
        title="Test Post",
        description="Test Description",
        read_length="3 min read",
        content="Test content",
        authors="Test Author",
        published=True
    )
    return post


def post_unpublished():
    post = Post.objects.create(
        title="Test Post",
        description="Test Description",
        read_length="3 min read",
        content="Test content",
        authors="Test Author",
        published=False
    )
    return post


def post_quotes():
    post = Post.objects.create(
        title="Test Post",
        description="Test Description",
        read_length="3 min read",
        content=unquoted_content,
        authors="Test Author",
        published=True
    )
    return post


class PostEditViewTests(TestCase):
    def setUp(self):
        user = User.objects.create(username="testuser")
        user.set_password("12345")
        user.save()
        self.client = Client()
        self.client.login(username="testuser", password="12345")

    def test_access(self):
        post = post_no_quotes()
        response = self.client.get((reverse("blog:edit", kwargs={"pk": post.id})))
        self.assertEqual(response.status_code, 200)

    def test_post_deleted_submission(self):
        post = post_no_quotes()
        id = post.id
        data = {
            "title": "Changed Title",
            "authors": "ChangedAuthor",
            "description": "Changed Description",
            "read_length": "5 min read",
            "content": "changed content"
        }
        post.delete()
        response = self.client.post(reverse("blog:edit", kwargs={"pk": id}), data)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "We couldn't find that post."
        )

    def test_successful_submission(self):
        post = post_no_quotes()
        data = {
            "title": "Changed Title",
            "authors": "ChangedAuthor",
            "description": "Changed Description",
            "read_length": "5 min read",
            "content": "changed content"
        }
        response = self.client.post(reverse("blog:edit", kwargs={"pk": post.id}), data)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "Article successfully edited."
        )
        post.refresh_from_db()
        self.assertEqual(post.title, "Changed Title")
        self.assertEqual(post.authors, "ChangedAuthor")
        self.assertEqual(post.description, "Changed Description")
        self.assertEqual(post.read_length, "5 min read")
        self.assertEqual(post.content, "changed content")

    def test_invalid_submission(self):
        post = post_no_quotes()
        data = {
            "title": "",
            "authors": "ChangedAuthor",
            "description": "Changed Description",
            "read_length": "5 min read",
            "content": "changed content"
        }
        response = self.client.post(reverse("blog:edit", kwargs={"pk": post.id}), data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "Please check the form for errors and try again."
        )


class PostCreateViewTests(TestCase):
    def setUp(self):
        user = User.objects.create(username="testuser")
        user.set_password("12345")
        user.save()
        self.client = Client()
        self.client.login(username="testuser", password="12345")

    def test_create_get(self):
        response = self.client.get(reverse("blog:create"))
        self.assertEqual(response.status_code, 200)

    def test_valid_submission(self):
        data = {
            "title": "Test Title",
            "authors": "TestAuthor",
            "description": "Test Description",
            "read_length": "3 min read",
            "content": "test content"
        }
        response = self.client.post(reverse("blog:create"), data)
        self.assertEqual(response.status_code, 302)

    def test_invalid_submission(self):
        data = {
            "title": "",
            "authors": "TestAuthor",
            "description": "Test Description",
            "read_length": "3 min read",
            "content": "test content"
        }
        response = self.client.post(reverse("blog:create"), data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "Please check the form for errors and try again."
        )


class PostIndexTests(TestCase):
    def setUp(self):
        user = User.objects.create(username="testuser")
        user.set_password("12345")
        user.save()
        self.client = Client()
        self.client.login(username="testuser", password="12345")

    def test_access(self):
        response = self.client.get(reverse("blog:blog-index"))
        self.assertEqual(response.status_code, 200)


class PostDashboardTests(TestCase):
    def setUp(self):
        user = User.objects.create(username="testuser")
        user.set_password("12345")
        user.save()
        self.client = Client()
        self.client.login(username="testuser", password="12345")

    def test_access(self):
        response = self.client.get(reverse("blog:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_delete_success(self):
        post = post_quotes()
        data = {
            "action": "delete",
            "pk": post.id,
        }
        response = self.client.post(reverse("blog:dashboard"), data)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "Article deleted successfully"
        )
        try:
            post.refresh_from_db()
        except Post.DoesNotExist:
            assert True
        except Exception as e:
            assert False

    def test_dashboard_delete_failure(self):
        post = post_quotes()
        data = {
            "action": "delete",
            "pk": post.id,
        }
        post.delete()
        response = self.client.post(reverse("blog:dashboard"), data)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "We couldn't find that article in the database."
        )

    def test_dashboard_publish(self):
        post = post_unpublished()
        data = {
            "action": "publish",
            "pk": post.id,
        }
        response = self.client.post(reverse("blog:dashboard"), data)
        post.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "Article published successfully."
        )
        self.assertEqual(post.publish_date.year, timezone.now().year)
        self.assertEqual(post.publish_date.month, timezone.now().month)
        self.assertEqual(post.publish_date.day, timezone.now().day)
        assert post.published

    def test_dashboard_unpublish(self):
        post = post_quotes()
        data = {
            "action": "publish",
            "pk": post.id,
        }
        response = self.client.post(reverse("blog:dashboard"), data)
        post.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "Article taken down from public view successfully."
        )
        self.assertEqual(post.publish_date, None)
        assert not post.published

    def test_dashboard_does_not_exist(self):
        post = post_quotes()
        data = {
            "action": "publish",
            "pk": post.id,
        }
        post.delete()
        response = self.client.post(reverse("blog:dashboard"), data)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "We couldn't find that article in the database."
        )

    def test_dashboard_unknown_command(self):
        post = post_quotes()
        data = {
            "action": "unknown",
            "pk": post.id,
        }
        post.delete()
        response = self.client.post(reverse("blog:dashboard"), data)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "The server had an issue. We aren't sure what happened."
        )


class PostDisplayViewTests(TestCase):
    def setUp(self):
        user = User.objects.create(username="testuser")
        user.set_password("12345")
        user.save()
        self.client = Client()
        self.client.login(username="testuser", password="12345")

    def test_unpublished(self):
        post = post_unpublished()
        response = self.client.get(reverse("blog:display", kwargs={"pk": post.id}))
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "That article isn't published yet."
        )

    def test_no_quotes(self):
        post = post_no_quotes()
        response = self.client.get(reverse("blog:display", kwargs={"pk": post.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['instance'].content, post.content)

    def test_quotes(self):
        post = post_quotes()
        response = self.client.get(reverse("blog:display", kwargs={"pk": post.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['instance'].content, quoted_content)

    def test_post_does_not_exist(self):
        post = post_no_quotes()
        id = post.id
        post.delete()
        response = self.client.get(reverse("blog:display", kwargs={"pk": id}))
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "That article no longer exists."
        )
