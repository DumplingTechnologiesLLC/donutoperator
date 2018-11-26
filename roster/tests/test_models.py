import pytest
from roster.models import Shooting, Tag, Source

@pytest.fixture
def valid_shooting():
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
	Tag.objects.bulk_create([
		Tag(text='tag1', shooting=shooting),
		Tag(text='tag2', shooting=shooting),
	])
	Source.objects.bulk_create([
		Source(text='source1', shooting=shooting),
		Source(text='source2', shooting=shooting),
	])
	return shooting


@pytest.fixture
def valid_shooting_no_name_no_city_no_age():
	shooting = Shooting.objects.create(
		name="",
		age=-1,
		race=1,
		gender=1,
		date="2018-11-10",
		description="",
		city="",
		state=1,
	)
	Tag.objects.bulk_create([
		Tag(text='tag1', shooting=shooting),
		Tag(text='tag2', shooting=shooting),
	])
	Source.objects.bulk_create([
		Source(text='source1', shooting=shooting),
		Source(text='source2', shooting=shooting),
	])
	return shooting


@pytest.fixture
def valid_tag():
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
	tag = Tag.objects.create(
		text='tag1',
		shooting=shooting,
	)
	return tag


@pytest.fixture
def valid_source():
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
	source = Source.objects.create(
		text='source1',
		shooting=shooting,
	)
	return source


@pytest.mark.django_db
def test_valid_shooting_as_dict(valid_shooting):
	shooting_as_dict = valid_shooting.as_dict()
	assert valid_shooting.age == shooting_as_dict["age"]
	assert len(shooting_as_dict['tags']) == 2
	assert len(shooting_as_dict['sources']) == 2


@pytest.mark.django_db
def test_valid_shooting_missing_parameters(valid_shooting_no_name_no_city_no_age):
	shooting_as_dict = valid_shooting_no_name_no_city_no_age.as_dict()
	assert shooting_as_dict["age"] == "No Age"
	assert shooting_as_dict["city"] == "Unknown"
	assert shooting_as_dict["video_url"] == "None"
	assert shooting_as_dict["unfiltered_video_url"] == "None"
	assert shooting_as_dict["description"] == ""


@pytest.mark.django_db
def test_valid_shooting_str(valid_shooting):
	assert str(valid_shooting) == "2018-11-10 Test Name"


@pytest.mark.django_db
def test_valid_tag_as_dict(valid_tag):
	tag_as_dict = valid_tag.as_dict()
	assert tag_as_dict["id"] == valid_tag.id
	assert tag_as_dict["text"] == valid_tag.text


@pytest.mark.django_db
def test_valid_tag_as_str(valid_tag):
	assert str(valid_tag) == valid_tag.text


@pytest.mark.django_db
def test_valid_source_as_dict(valid_source):
	source_as_dict = valid_source.as_dict()
	assert source_as_dict["id"] == valid_source.id
	assert source_as_dict["text"] == valid_source.text


@pytest.mark.django_db
def test_valid_source_as_str(valid_source):
	assert str(valid_source) == valid_source.text
