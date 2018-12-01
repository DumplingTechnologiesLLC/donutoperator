import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from roster.models import Shooting, Tag
from django.urls import reverse
import datetime
import json

invalid_video = "https://youtu.be/IaWgcgYj690"
valid_video = "https://www.youtube.com/watch?v=IaWgcgYj690"


class DeleteShootingViewTests(TestCase):
	def setUp(self):
		user = User.objects.create(username="testuser")
		user.set_password("12345")
		user.save()
		self.client = Client()
		self.client.login(username="testuser", password="12345")

	def test_successful_submission(self):
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
		response = self.client.post(
			reverse("roster:delete-killing"), {"id": shooting.id})
		self.assertEqual(response.status_code, 200)
		try:
			shooting.refresh_from_db()
		except Shooting.DoesNotExist:
			pass
		except Exception as e:
			print(str(e))
			assert False

	def test_unsuccessful_submission(self):
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
		id = shooting.id
		shooting.delete()
		response = self.client.post(reverse("roster:delete-killing"), {"id": id})
		self.assertEqual(response.status_code, 500)


class EditShootingViewTests(TestCase):
	def setUp(self):
		user = User.objects.create(username="testuser")
		user.set_password("12345")
		user.save()
		self.client = Client()
		self.client.login(username="testuser", password="12345")

	def test_successful_submission(self):
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
		Tag.objects.create(
			text="tag1",
			shooting=shooting
		)
		self.assertEqual(shooting.tags.all().count(), 1)
		self.assertEqual(shooting.sources.all().count(), 0)
		shooting_as_dict = {
			"id": shooting.id,
			"name": "Changed Name",
			"age": 20,
			"race": 2,
			"gender": 2,
			"date": "2018-10-11",
			"description": "Changec Description",
			"city": "Changed City",
			"state": 1,
			"tags": ["tag1", "tag2"],
			"sources": ["source1", "source2"],
			"video_url": valid_video,
		}
		data = {
			"shooting": json.dumps(shooting_as_dict)
		}
		response = self.client.post(reverse("roster:edit-killing"), data)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(int(response.content.decode('utf-8')), shooting.id)
		shooting.refresh_from_db()
		self.assertEqual(shooting.name, "Changed Name")
		self.assertEqual(shooting.age, 20)
		self.assertEqual(shooting.race, 2)
		self.assertEqual(shooting.gender, 2)
		self.assertEqual(str(shooting.date), "2018-10-11")
		self.assertEqual(shooting.description, "Changec Description")
		self.assertEqual(shooting.city, "Changed City")
		self.assertEqual(shooting.state, 1)
		self.assertEqual(shooting.tags.all().count(), 2)
		self.assertEqual(shooting.sources.all().count(), 2)
		self.assertEqual(shooting.unfiltered_video_url, valid_video)

	def test_no_age_successful(self):
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
		Tag.objects.create(
			text="tag1",
			shooting=shooting
		)
		self.assertEqual(shooting.tags.all().count(), 1)
		self.assertEqual(shooting.sources.all().count(), 0)
		shooting_as_dict = {
			"id": shooting.id,
			"name": "Changed Name",
			"age": "",
			"race": 2,
			"gender": 2,
			"date": "2018-10-11",
			"description": "Changec Description",
			"city": "Changed City",
			"state": 1,
			"tags": ["tag1", "tag2"],
			"sources": ["source1", "source2"],
			"video_url": valid_video,
		}
		data = {
			"shooting": json.dumps(shooting_as_dict)
		}
		response = self.client.post(reverse("roster:edit-killing"), data)
		self.assertEqual(response.status_code, 200)
		shooting.refresh_from_db()
		self.assertEqual(shooting.age, -1)

	def test_bad_age(self):
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
		Tag.objects.create(
			text="tag1",
			shooting=shooting
		)
		self.assertEqual(shooting.tags.all().count(), 1)
		self.assertEqual(shooting.sources.all().count(), 0)
		shooting_as_dict = {
			"id": shooting.id,
			"name": "Changed Name",
			"age": -1,
			"race": 2,
			"gender": 2,
			"date": "2018-10-11",
			"description": "Changec Description",
			"city": "Changed City",
			"state": 1,
			"tags": ["tag1", "tag2"],
			"sources": ["source1", "source2"],
			"video_url": valid_video,
		}
		data = {
			"shooting": json.dumps(shooting_as_dict)
		}
		response = self.client.post(reverse("roster:edit-killing"), data)
		self.assertEqual(response.status_code, 400)
		self.assertEqual(
			response.content.decode("utf-8"),
			"Please provide a positive number for the age"
		)

	def test_shooting_does_not_exist(self):
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
		id = shooting.id
		shooting.delete()
		shooting_as_dict = {
			"id": id,
			"name": "Changed Name",
			"age": 1,
			"race": 2,
			"gender": 2,
			"date": "2018-10-11",
			"description": "Changec Description",
			"city": "Changed City",
			"state": 1,
			"tags": ["tag1", "tag2"],
			"sources": ["source1", "source2"],
			"video_url": valid_video,
		}
		data = {
			"shooting": json.dumps(shooting_as_dict)
		}
		response = self.client.post(reverse("roster:edit-killing"), data)
		self.assertEqual(response.status_code, 500)

	def test_invalid_form(self):
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
		Tag.objects.create(
			text="tag1",
			shooting=shooting
		)
		self.assertEqual(shooting.tags.all().count(), 1)
		self.assertEqual(shooting.sources.all().count(), 0)
		shooting_as_dict = {
			"id": shooting.id,
			"name": "Changed Name",
			"age": 1,
			"race": 2,
			"gender": 2,
			"date": "2018-10-11",
			"description": "Changec Description",
			"city": "Changed City",
			"state": 1,
			"tags": ["tag1", "tag2"],
			"sources": ["source1", "source2"],
			"video_url": invalid_video,
		}
		data = {
			"shooting": json.dumps(shooting_as_dict)
		}
		response = self.client.post(reverse("roster:edit-killing"), data)
		self.assertEqual(response.status_code, 400)


class SubmitShootingViewTests(TestCase):
	def setUp(self):
		user = User.objects.create(username="testuser")
		user.set_password("12345")
		user.save()
		self.client = Client()
		self.client.login(username="testuser", password="12345")

	def test_successful_submission(self):
		shooting = {
			"name": "Test Name",
			"age": 21,
			"race": 1,
			"gender": 1,
			"date": "2018-10-11",
			"description": "Test Description",
			"city": "Test City",
			"state": 1,
			"tags": ["tag1", "tag2"],
			"sources": ["source1", "source2"],
			"video_url": valid_video,
		}
		data = {
			"shooting": json.dumps(shooting)
		}
		response = self.client.post(reverse("roster:submit-killing"), data)
		self.assertEqual(response.status_code, 200)
		id = int(response.content)
		shooting = Shooting.objects.get(pk=id)
		self.assertEqual(shooting.unfiltered_video_url, valid_video)
		self.assertEqual(shooting.tags.all().count(), 2)
		self.assertEqual(shooting.sources.all().count(), 2)
		assert "iframe" in shooting.video_url

	def test_no_age_submission(self):
		shooting = {
			"name": "Test Name",
			"age": "",
			"race": 1,
			"gender": 1,
			"date": "2018-10-11",
			"description": "Test Description",
			"city": "Test City",
			"state": 1,
			"tags": ["tag1", "tag2"],
			"sources": ["source1", "source2"],
			"video_url": valid_video,
		}
		data = {
			"shooting": json.dumps(shooting)
		}
		response = self.client.post(reverse("roster:submit-killing"), data)
		self.assertEqual(response.status_code, 200)
		id = int(response.content)
		shooting = Shooting.objects.get(pk=id)
		self.assertEqual(shooting.unfiltered_video_url, valid_video)
		self.assertEqual(shooting.age, -1)
		assert "iframe" in shooting.video_url

	def test_bad_url_submission(self):
		shooting = {
			"name": "Test Name",
			"age": 21,
			"race": 1,
			"gender": 1,
			"date": "2018-10-11",
			"description": "Test Description",
			"city": "Test City",
			"state": 1,
			"tags": ["tag1", "tag2"],
			"sources": ["source1", "source2"],
			"video_url": invalid_video,
		}
		data = {
			"shooting": json.dumps(shooting)
		}
		response = self.client.post(reverse("roster:submit-killing"), data)
		self.assertEqual(response.status_code, 400)

	def test_bad_age_submission(self):
		shooting = {
			"name": "Test Name",
			"age": -1,
			"race": 1,
			"gender": 1,
			"date": "2018-10-11",
			"description": "Test Description",
			"city": "Test City",
			"state": 1,
			"tags": ["tag1", "tag2"],
			"sources": ["source1", "source2"],
			"video_url": valid_video,
		}
		data = {
			"shooting": json.dumps(shooting)
		}
		response = self.client.post(reverse("roster:submit-killing"), data)
		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.content.decode("utf-8"),
						 "Please provide a positive number for the age")


class RosterListViewTests(TestCase):
	def setUp(self):
		current_year = datetime.date.today().strftime("%Y-%m-%d")
		Shooting.objects.bulk_create([
			Shooting(
				name="Test Name",
				age=21,
				race=1,
				gender=1,
				date=current_year,
				description="Test Description",
				city="Test City",
				state=1,
			),
			Shooting(
				name="Test Name1",
				age=21,
				race=1,
				gender=1,
				date=current_year,
				description="Test Description",
				city="Test City",
				state=1,
			),
			Shooting(
				name="Test Name2",
				age=21,
				race=1,
				gender=1,
				date=current_year,
				description="Test Description",
				city="Test City",
				state=1,
			),
			Shooting(
				name="Test Name3",
				age=21,
				race=1,
				gender=1,
				date="2017-11-10",
				description="Test Description",
				city="Test City",
				state=1,
			),
			Shooting(
				name="Test Name4",
				age=21,
				race=1,
				gender=1,
				date="2017-11-10",
				description="Test Description",
				city="Test City",
				state=1,
			),
			Shooting(
				name="Test Name5",
				age=21,
				race=1,
				gender=1,
				date="2017-11-10",
				description="Test Description",
				city="Test City",
				state=1,
			),
		])
		self.client = Client()

	def test_success_get(self):
		response = self.client.get(reverse("roster:index"))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.context["shootings"]), 3)

	def test_success_get_with_date(self):
		response = self.client.get(reverse("roster:date-index", kwargs={"date": 2017}))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.context["shootings"]), 3)
		for shooting in response.context["shootings"]:
			self.assertEqual(shooting["date"], "2017-11-10")
