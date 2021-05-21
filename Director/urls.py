from django.urls import path

from Director.views import DirectorViews, DirectorDetail, DirectorAdd

app_name = 'directors'

urlpatterns = [
    path('', DirectorViews.as_view(), name='directors'),
    path('detail/<int:pk>/', DirectorDetail.as_view(), name='detail_directors'),
    path('add/', DirectorAdd.as_view(), name='add_directors'),

]
