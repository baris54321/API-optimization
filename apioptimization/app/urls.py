from django.urls import path
from .views import UserDetailV1, UserDetailV2, UserList
    
urlpatterns = [ 
    path('users/', UserList.as_view(), name='user-list'),
    path('users/v1/<int:pk>/', UserDetailV1.as_view(), name='user-detail-v1'),  #Time taken: 17 second


]
