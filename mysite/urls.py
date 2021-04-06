from django.contrib import admin
from django.urls import path, include

from Company.views import CompanyViews
from Director.views import DirectorViews, HomeViews

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', HomeViews.as_view(), name='home'),
    path('directors/', include('Director.urls')),
    path('company/', include('Company.urls')),
    path('', include('bank.urls')),
]
