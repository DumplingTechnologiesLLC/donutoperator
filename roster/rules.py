import rules
from django.contrib.auth.models import Group


@rules.predicate
def can_edit_shooting(user, shooting):
	group, created = Group.objects.get_or_create(
		name="SuperCurators",
	)
	if user in group.user_set.all():
		return True
	elif user in shooting.specially_exempted_users.all():
		return True
	elif shooting.created_by == user:
		return True
	return False


@rules.predicate
def can_edit_bodycam(user, bodycam):
	group, created = Group.objects.get_or_create(
		name="SuperCurators",
	)
	if user in group.user_set.all():
		return True
	elif user in bodycam.specially_exempted_users.all():
		return True
	elif bodycam.created_by == user:
		return True
	return False


@rules.predicate
def can_make_articles(user):
	group, created = Group.objects.get_or_create(
		name="SuperCurators",
	)
	if user in group.user_set.all():
		return True
	return False


rules.add_rule("core.can_edit_shooting", can_edit_shooting)
rules.add_rule("core.can_edit_bodycam", can_edit_bodycam)
rules.add_rule("core.can_make_articles", can_make_articles)
rules.add_perm("core.can_edit_shooting", can_edit_shooting)
rules.add_perm("core.can_edit_bodycam", can_edit_bodycam)
rules.add_perm("core.can_make_articles", can_make_articles)
