import pytest
from bodycams.forms import BodycamModelForm


@pytest.fixture
def valid_bodycam():
    data = {
        "bodycam": {
            "id": "",
            "title": "Test Title",
            "video": "<iframe width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/NkLb-0-L5OA\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>",
            "description": "Test Description",
            "department": "Test Department",
            "state": "1",
            "city": "Test City",
                    "date": "2018-11-10",
                    "tags": [],
                    "shooting": ""
        }
    }
    return data


@pytest.fixture
def valid_no_dimensions_bodycam():
    data = {
        "bodycam": {
            "id": "",
            "title": "Test Title",
            "video": "<iframe src=\"https://www.youtube.com/embed/NkLb-0-L5OA\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>",
            "description": "Test Description",
            "department": "Test Department",
            "state": "1",
            "city": "Test City",
                    "date": "2018-11-10",
                    "tags": [],
                    "shooting": ""
        }
    }
    return data


@pytest.fixture
def invalid_video_bodycam():
    data = {
        "bodycam": {
            "id": "",
            "title": "Test Title",
            "video": "asdf",
            "description": "Test Description",
            "department": "Test Department",
            "state": "1",
            "city": "Test City",
                    "date": "2018-11-10",
                    "tags": [],
                    "shooting": ""
        }
    }
    return data


def assert_url_equality(video_url):
    video1 = "<iframe width='100%' height='100%' src=\"https://www.youtube.com/embed/NkLb-0-L5OA\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>"
    video2 = "<iframe width=\"100%\" height=\"100%\" src=\"https://www.youtube.com/embed/NkLb-0-L5OA\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>"
    video3 = "<iframe width=\'100%\' height=\"100%\" src=\"https://www.youtube.com/embed/NkLb-0-L5OA\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>"
    return (video_url == video1 or video_url == video2 or video_url == video3)


@pytest.mark.django_db
def test_bodycam_form_correct(valid_bodycam):
    form = BodycamModelForm(valid_bodycam["bodycam"])
    form.is_valid()
    print(form._errors)
    assert form.is_valid()
    bodycam = form.save()
    assert bodycam.title == "Test Title"
    assert assert_url_equality(bodycam.video)


@pytest.mark.django_db
def test_bodycam_no_dimensions_form_correct(valid_no_dimensions_bodycam):
    form = BodycamModelForm(valid_no_dimensions_bodycam["bodycam"])
    assert form.is_valid()
    bodycam = form.save()
    assert bodycam.title == "Test Title"
    assert "width='100%'" in bodycam.video
    assert "height='100%'" in bodycam.video


@pytest.mark.django_db
def test_bodycam_form_invalid(invalid_video_bodycam):
    form = BodycamModelForm(invalid_video_bodycam["bodycam"])
    assert not form.is_valid()
    found = False
    for key, error in form.errors.items():
        if "The video input MUST be an embed code" in error:
            found = True
    assert found
