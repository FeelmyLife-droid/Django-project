from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('directors/', include('Director.urls')),
    path('company/', include('Company.urls')),
    path('', include('bank.urls')),
    path('webhooks/', include('webhooks.urls')),

]
