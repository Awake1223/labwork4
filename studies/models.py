from django.db import models

# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    year = models.IntegerField()

    def __str__(self):
        return f"{self.title} - {self.author} ({self.year})"