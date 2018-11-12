import pytest
from blog.forms import PostForm


@pytest.fixture
def valid_form_data():
    return {
        "title": "Test Title",
        "authors": "TestAuthor",
        "description": "Test Description",
        "read_length": "3 min read",
        "content": "test content"
    }


@pytest.mark.django_db
def test_valid_form_submission(valid_form_data):
    form = PostForm(valid_form_data)
    assert form.is_valid()
    post = form.save()
    assert post.title == "Test Title"
    assert post.authors == "TestAuthor"
    assert post.description == "Test Description"
    assert post.read_length == "3 min read"
    assert post.content == "test content"
