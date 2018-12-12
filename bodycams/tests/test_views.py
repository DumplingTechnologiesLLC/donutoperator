import pytest
import json
from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User
from bodycams.models import Bodycam
from roster.models import Shooting, Tag
import datetime
from django.contrib.messages import get_messages

video_iframe = "<iframe width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/NkLb-0-L5OA\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>"


def correct_data():
	bodycam = {
		"id": "",
		"title": "Test Title Specifically For Test 123123123123123",
		"video": video_iframe,
		"description": "Test Description",
		"department": "Test Department",
		"state": "1",
		"city": "Test City",
		"date": "2018-11-10T03:15:32.696Z",
		"tags": ["TestTag", "TestTag2"],
		"shooting": ""
	}
	data = {
		"bodycam": json.dumps(bodycam)
	}
	return data


def invalid_data():
	bodycam = {
		"id": "",
		"title": "Test Title Specifically For Test 123123123123123",
		"video": video_iframe,
		"description": "Test Description",
		"department": "Test Department",
		"state": "",
		"city": "Test City",
		"date": "2018-11-10T03:15:32.696Z",
		"tags": ["TestTag", "TestTag2"],
		"shooting": ""
	}
	data = {
		"bodycam": json.dumps(bodycam)
	}
	return data


class BodycamLinkTests(TestCase):
	def setUp(self):
		user = User.objects.create(username="testuser")
		user.set_password("12345")
		user.save()
		self.client = Client()
		self.client.login(username="testuser", password="12345")

	def test_object_doesnt_exist(self):
		bodycam = Bodycam.objects.create(
			title="Test Title",
			video=video_iframe,
			description="Test Description",
			department="Test Department",
			state=1,
			date="2018-11-10",
		)
		response = self.client.post(reverse("bodycams:link-bodycam-shooting"), {
			"bodycam_id": "{}".format(bodycam.id),
			"shooting_id": "-1",
		})
		bodycam.refresh_from_db()
		self.assertEqual(response.status_code, 500)
		self.assertEqual(bodycam.shooting, None)

	def test_successful_link(self):
		bodycam = Bodycam.objects.create(
			title="Test Title",
			video=video_iframe,
			description="Test Description",
			department="Test Department",
			state=1,
			date="2018-11-10",
		)
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
		response = self.client.post(reverse("bodycams:link-bodycam-shooting"), {
			"bodycam_id": "{}".format(bodycam.id),
			"shooting_id": "{}".format(shooting.id),
		})
		bodycam.refresh_from_db()
		shooting.refresh_from_db()
		self.assertEqual(response.status_code, 200)
		self.assertEqual(bodycam.shooting.id, shooting.id)
		self.assertEqual(shooting.bodycam().id, bodycam.id)


class BodycamEditTests(TestCase):
	def setUp(self):
		user = User.objects.create(username="testuser")
		user.set_password("12345")
		user.save()
		self.client = Client()
		self.client.login(username="testuser", password="12345")

	def test_successful_edit_with_unlink(self):
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
			title='TEST',
			video=video_iframe,
			state=1,
			date="2018-01-01",
			shooting=shooting
		)
		tag = Tag.objects.create(text="Test")
		tag.bodycams.add(bodycam)
		self.assertEqual(bodycam.tags.all().count(), 1)
		self.assertEqual(bodycam.shooting, shooting)
		bodycam_as_dict = {
			"id": bodycam.id,
			"title": "Changed Title",
			"video": video_iframe,
			"description": "Test Description",
			"department": "Test Department",
			"state": "1",
			"city": "Test City",
			"date": "2018-11-10T03:15:32.696Z",
			"tags": ["TestTag", "TestTag2"],
			"shooting": -1
		}
		data = {
			"bodycam": json.dumps(bodycam_as_dict)
		}
		response = self.client.post(reverse("bodycams:bodycam-edit"), data)
		bodycam.refresh_from_db()
		self.assertEqual(response.status_code, 200)
		self.assertEqual(bodycam.tags.all().count(), 2)
		self.assertEqual(bodycam.title, "Changed Title")
		self.assertEqual(None, bodycam.shooting)

	def test_successful_edit_with_shooting(self):
		bodycam = Bodycam.objects.create(
			title='TEST',
			video=video_iframe,
			state=1,
			date="2018-01-01"
		)
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
		tag = Tag.objects.create(text="Test")
		tag.bodycams.add(bodycam)
		self.assertEqual(bodycam.tags.all().count(), 1)
		bodycam_as_dict = {
			"id": bodycam.id,
			"title": "Changed Title",
			"video": video_iframe,
			"description": "Test Description",
			"department": "Test Department",
			"state": "1",
			"city": "Test City",
			"date": "2018-11-10T03:15:32.696Z",
			"tags": ["TestTag", "TestTag2"],
			"shooting": shooting.id
		}
		data = {
			"bodycam": json.dumps(bodycam_as_dict)
		}
		response = self.client.post(reverse("bodycams:bodycam-edit"), data)
		bodycam.refresh_from_db()
		self.assertEqual(response.status_code, 200)
		self.assertEqual(bodycam.tags.all().count(), 2)
		self.assertEqual(bodycam.title, "Changed Title")
		self.assertEqual(shooting, bodycam.shooting)

	def test_successful_edit(self):
		bodycam = Bodycam.objects.create(
			title='TEST',
			video=video_iframe,
			state=1,
			date="2018-01-01"
		)
		tag = Tag.objects.create(text="Test")
		tag.bodycams.add(bodycam)
		self.assertEqual(bodycam.tags.all().count(), 1)
		bodycam_as_dict = {
			"id": bodycam.id,
			"title": "Changed Title",
			"video": video_iframe,
			"description": "Test Description",
			"department": "Test Department",
			"state": "1",
			"city": "Test City",
			"date": "2018-11-10T03:15:32.696Z",
			"tags": ["TestTag", "TestTag2"],
			"shooting": ""
		}
		data = {
			"bodycam": json.dumps(bodycam_as_dict)
		}
		response = self.client.post(reverse("bodycams:bodycam-edit"), data)
		bodycam.refresh_from_db()
		self.assertEqual(response.status_code, 200)
		self.assertEqual(bodycam.tags.all().count(), 2)
		self.assertEqual(bodycam.title, "Changed Title")

	def test_bad_edit(self):
		bodycam = Bodycam.objects.create(
			title='TEST',
			video=video_iframe,
			state=1,
			date="2018-01-01"
		)
		tag = Tag.objects.create(text="Test")
		tag.bodycams.add(bodycam)
		self.assertEqual(bodycam.tags.all().count(), 1)
		bodycam_as_dict = {
			"id": bodycam.id,
			"title": "Changed Title",
			"video": "",
			"description": "Test Description",
			"department": "Test Department",
			"state": "1",
			"city": "Test City",
			"date": "2018-11-10T03:15:32.696Z",
			"tags": ["TestTag", "TestTag2"],
			"shooting": ""
		}
		data = {
			"bodycam": json.dumps(bodycam_as_dict)
		}
		response = self.client.post(reverse("bodycams:bodycam-edit"), data)
		bodycam.refresh_from_db()
		self.assertEqual(response.status_code, 400)
		self.assertEqual(bodycam.tags.all().count(), 1)
		self.assertEqual(bodycam.title, "TEST")

	def test_link_race_condition(self):
		bodycam = Bodycam.objects.create(
			title='TEST',
			video=video_iframe,
			state=1,
			date="2018-01-01"
		)
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
		tag = Tag.objects.create(text="Test")
		tag.bodycams.add(bodycam)
		self.assertEqual(bodycam.tags.all().count(), 1)
		id = shooting.id
		bodycam_as_dict = {
			"id": bodycam.id,
			"title": "Changed Title",
			"video": video_iframe,
			"description": "Test Description",
			"department": "Test Department",
			"state": "1",
			"city": "Test City",
			"date": "2018-11-10T03:15:32.696Z",
			"tags": ["TestTag", "TestTag2"],
			"shooting": id
		}
		shooting.delete()
		data = {
			"bodycam": json.dumps(bodycam_as_dict)
		}
		response = self.client.post(reverse("bodycams:bodycam-edit"), data)
		self.assertEqual(response.status_code, 406)
		self.assertEqual(
			response.content.decode("utf-8"),
			("We've created the bodycam but when we tried to link the bodycam"
			" to the shooting you requested, we couldn't find the shooting. "
			"Please refresh the page and try to link the bodycam manually."))

	def test_race_condition(self):
		bodycam = Bodycam.objects.create(
			title='TEST',
			video=video_iframe,
			state=1,
			date="2018-01-01"
		)
		id = bodycam.id
		# supposing this gets deleted by another user while its being edited
		bodycam.delete()
		bodycam_as_dict = {
			"id": id,
			"title": "Changed Title",
			"video": "",
			"description": "Test Description",
			"department": "Test Department",
			"state": "1",
			"city": "Test City",
			"date": "2018-11-10T03:15:32.696Z",
			"tags": ["TestTag", "TestTag2"],
			"shooting": ""
		}
		data = {
			"bodycam": json.dumps(bodycam_as_dict)
		}
		response = self.client.post(reverse("bodycams:bodycam-edit"), data)
		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.content.decode("utf-8"),
						 "We couldn't find that bodycam in our database anymore.")


class BodycamDashboardTests(TestCase):
	def setUp(self):
		user = User.objects.create(username="testuser")
		user.set_password("12345")
		user.save()
		self.client = Client()
		self.client.login(username="testuser", password="12345")

	def test_success_get(self):
		response = self.client.get(reverse("bodycams:dashboard"))
		self.assertEqual(response.status_code, 200)

	def test_delete_success(self):
		bodycam = Bodycam.objects.create(
			title='TEST',
			video=video_iframe,
			state=1,
			date="2018-01-01"
		)
		data = {
			"pk": bodycam.id
		}
		response = self.client.post(reverse("bodycams:dashboard"), data)
		self.assertEqual(response.status_code, 302)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(
			str(messages[0]),
			"Bodycam deleted successfully"
		)

	def test_delete_failure(self):
		bodycam = Bodycam.objects.create(
			title='TEST',
			video=video_iframe,
			state=1,
			date="2018-01-01"
		)
		id = bodycam.id
		bodycam.delete()
		data = {
			"pk": id
		}
		response = self.client.post(reverse("bodycams:dashboard"), data)
		self.assertEqual(response.status_code, 302)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(
			str(messages[0]),
			"We couldn't find that bodycam in the database."
		)


class BodycamIndexTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_success_get(self):
		response = self.client.get(reverse("bodycams:bodycams"))
		self.assertEqual(response.status_code, 200)

	def test_get_with_date(self):
		current_date_as_year = datetime.date.today().strftime("%Y-%m-%d")
		Bodycam.objects.bulk_create([
			Bodycam(
				title='TEST',
				video=video_iframe,
				state=1,
				date=current_date_as_year
			),
			Bodycam(
				title='TEST1',
				video=video_iframe,
				state=1,
				date=current_date_as_year
			),
			Bodycam(
				title='TEST3',
				video=video_iframe,
				state=1,
				date=current_date_as_year
			),
			Bodycam(
				title='TEST4',
				video=video_iframe,
				state=1,
				date="2017-01-01",
			),
			Bodycam(
				title='TEST5',
				video=video_iframe,
				state=1,
				date="2017-01-01",
			),
			Bodycam(
				title='TEST6',
				video=video_iframe,
				state=1,
				date="2017-01-01",
			),
		])
		response = self.client.get(reverse('bodycams:date-index', kwargs={"date": 2017}))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.context["bodycams"]), 3)


class BodycamSubmitTests(TestCase):
	def setUp(self):
		user = User.objects.create(username="testuser")
		user.set_password("12345")
		user.save()
		self.client = Client()
		self.client.login(username="testuser", password="12345")

	def test_successful_submission(self):
		response = self.client.post(reverse("bodycams:bodycam-submit"), correct_data())
		self.assertEqual(response.status_code, 200)
		bodycam = Bodycam.objects.get(
			title="Test Title Specifically For Test 123123123123123")
		self.assertEqual(bodycam.id, int(response.content))
		self.assertEqual(bodycam.tags.all().count(), 2)

	def test_bad_submission(self):
		response = self.client.post(reverse("bodycams:bodycam-submit"), invalid_data())
		self.assertEqual(response.status_code, 400)

	def test_connected_shooting(self):
		data = correct_data()
		bodycam_as_dict = json.loads(data["bodycam"])
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
		bodycam_as_dict["shooting"] = shooting.id
		data["bodycam"] = json.dumps(bodycam_as_dict)
		response = self.client.post(reverse("bodycams:bodycam-submit"), data)
		self.assertEqual(response.status_code, 200)
		bodycam = Bodycam.objects.get(pk=int(response.content))
		self.assertEqual(bodycam.shooting, shooting)

	def test_connected_race_condition_shooting(self):
		data = correct_data()
		bodycam_as_dict = json.loads(data["bodycam"])
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
		bodycam_as_dict["shooting"] = shooting.id
		data["bodycam"] = json.dumps(bodycam_as_dict)
		# shooting gets deleted by another user
		shooting.delete()
		response = self.client.post(reverse("bodycams:bodycam-submit"), data)
		self.assertEqual(response.status_code, 406)
		self.assertEqual(response.content.decode("utf-8"),
						 "We've created the bodycam but when we tried to link the bodycam to the shooting you requested, we couldn't find the shooting. Please refresh the page and try to link the bodycam manually.")
