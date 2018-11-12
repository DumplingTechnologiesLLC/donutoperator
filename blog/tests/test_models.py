import pytest
from blog.models import Post

@pytest.fixture
def test_published_post():
	post = Post.objects.create(
		title="Test Post",
		description="Test Description",
		read_length="3 min read",
		content="<span class='text-muted'>test whatever</span>",
		authors="Test Author",
	)
	return post

@pytest.mark.django_db
def test_post_as_str(test_published_post):
	assert str(test_published_post) == "Test Post"
