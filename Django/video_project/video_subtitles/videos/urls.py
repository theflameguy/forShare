from django.urls import path
from .views import upload_video, search_video,video_list,search_subtitle

urlpatterns = [
    path('upload/', upload_video, name='upload_video'),
    path('search/<int:id>', search_video, name='search_video'),
    path('video_list/', video_list, name='video_list'),
    path('search_subtitle/', search_subtitle, name='search_subtitle'),

]
