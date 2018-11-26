import pytest
import datetime
from bodycams.models import Bodycam
from roster.models import Shooting

video = "<iframe width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/NkLb-0-L5OA\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>"


@pytest.fixture
def valid_bodycam():
    bodycam = Bodycam.objects.create(
        title="Test Title",
        video=video,
        description="Test Description",
        department="Test Department",
        state=1,
        date=datetime.date.today(),
        city="Test City",
    )
    return bodycam


@pytest.fixture
def valid_bodycam_with_shooting():
    shooting = Shooting.objects.create(
        name="Test Name",
        age=21,
        race=1,
        gender=1,
        date="2018-11-10",
        description="Test Description",
        city="Test City",
        state=1,
    )
    bodycam = Bodycam.objects.create(
        title="Test Title",
        video=video,
        description="Test Description",
        department="Test Department",
        state=1,
        date=datetime.date.today(),
        city="Test City",
        shooting=shooting,
    )
    return bodycam


@pytest.mark.django_db
def test_bodycams_as_dict(valid_bodycam_with_shooting):
    bodycam = valid_bodycam_with_shooting
    shooting = bodycam.shooting
    bodycam_dict = bodycam.as_dict()
    assert bodycam_dict["shooting"] == shooting.as_dict()


@pytest.mark.django_db
def test_bodycam_as_str(valid_bodycam):
    bodycam = valid_bodycam
    assert bodycam.title == str(bodycam)
