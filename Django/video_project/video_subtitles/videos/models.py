from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='videos/')
    created_at = models.DateTimeField(auto_now_add=True)

class Subtitle(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='subtitles')
    language = models.CharField(max_length=10)
    content = models.TextField()
    file = models.FileField(upload_to='srt_files/',null=True)
    created_at = models.DateTimeField(auto_now_add=True)
