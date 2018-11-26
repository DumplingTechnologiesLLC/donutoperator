import pytest
from roster.forms import ShootingModelForm


@pytest.fixture
def valid_shooting():
	data = {
		"shooting": {
			"id": "",
			"name": "Test Name",
			"date": "2018-11-11",
			"race": 1,
			"age": 20,
			"gender": 1,
			"state": 1,
			"city": "Test City",
			"video_url": "https://www.youtube.com/watch?v=IaWgcgYj690",
			"sources": ["source1", "source2", "source3"],
			"description": "Test Description",
			"tags": ["tag1", "tag2", "tag3"]
		}
	}
	return data


@pytest.fixture
def valid_shooting_no_url():
	data = {
		"shooting": {
			"id": "",
			"name": "Test Name",
			"date": "2018-11-11",
			"race": 1,
			"age": 20,
			"gender": 1,
			"state": 1,
			"city": "Test City",
			"video_url": "",
			"sources": ["source1", "source2", "source3"],
			"description": "Test Description",
			"tags": ["tag1", "tag2", "tag3"]
		}
	}
	return data


@pytest.fixture
def valid_shooting_no_name_no_city():
	data = {
		"shooting": {
			"id": "",
			"name": "",
			"date": "2018-11-11",
			"race": 1,
			"age": 20,
			"gender": 1,
			"state": 1,
			"city": "",
			"video_url": "",
			"sources": ["source1", "source2", "source3"],
			"description": "Test Description",
			"tags": ["tag1", "tag2", "tag3"]
		}
	}
	return data


@pytest.fixture
def invalid_url_shooting():
	data = {
		"shooting": {
			"id": "",
			"name": "",
			"date": "2018-11-11",
			"race": 1,
			"age": 20,
			"gender": 1,
			"state": 1,
			"city": "",
			"video_url": "https://youtu.be/IaWgcgYj690",
			"sources": ["source1", "source2", "source3"],
			"description": "Test Description",
			"tags": ["tag1", "tag2", "tag3"]
		}
	}
	return data


@pytest.mark.django_db
def test_valid_submission(valid_shooting):
	data = valid_shooting
	form = ShootingModelForm(data["shooting"])
	assert form.is_valid()
	shooting = form.save()
	assert shooting.name == "Test Name"
	assert shooting.date.strftime("%Y-%m-%d") == "2018-11-11"
	pre = '<iframe width="100%" height="315" src="https://www.youtube.com/embed/'
	post = '" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>'
	formatted_video = pre + "IaWgcgYj690" + post
	assert shooting.video_url == formatted_video


@pytest.mark.django_db
def test_valid_submission_no_url(valid_shooting_no_url):
	data = valid_shooting_no_url
	form = ShootingModelForm(data["shooting"])
	assert form.is_valid()
	shooting = form.save()
	assert shooting.name == "Test Name"
	assert shooting.date.strftime("%Y-%m-%d") == "2018-11-11"


@pytest.mark.django_db
def test_no_name_no_city_submission(valid_shooting_no_name_no_city):
	data = valid_shooting_no_name_no_city
	form = ShootingModelForm(data["shooting"])
	assert form.is_valid()
	shooting = form.save()
	assert shooting.name == "No Name"
	assert shooting.city == "Unknown"
	assert shooting.date.strftime("%Y-%m-%d") == "2018-11-11"


@pytest.mark.django_db
def test_invalid_url_submission(invalid_url_shooting):
	data = invalid_url_shooting
	form = ShootingModelForm(data["shooting"])
	assert not form.is_valid()
	found = False
	for key, error in form.errors.items():
		if "Please provide a valid video URL" in error:
			found = True
	assert found
