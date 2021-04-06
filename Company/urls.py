from django.urls import path

from Company.views import CompanyViews, CompanyDetail, CompanyAdd, CompanyDelete

app_name = 'company'

urlpatterns = [
    path('', CompanyViews.as_view(), name='company'),
    path('detail/<int:pk>/', CompanyDetail.as_view(), name='detail_company'),
    path('add/', CompanyAdd.as_view(), name='add_company'),
    path('delete/<int:pk>/', CompanyDelete.as_view(), name='delete_company'),
]
