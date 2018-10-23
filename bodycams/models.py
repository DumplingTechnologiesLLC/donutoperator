from django.db import models

# Create your models here.

class Bodycam(models.Model):
	title = models.CharField(max_length=120)