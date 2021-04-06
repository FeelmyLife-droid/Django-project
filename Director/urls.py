from django.urls import path

from Director.views import DirectorViews, DirectorDetail

app_name = 'directors'

urlpatterns = [
    path('', DirectorViews.as_view(), name='directors'),
    path('detail/<int:pk>/', DirectorDetail.as_view(), name='detail_directors'),

]
