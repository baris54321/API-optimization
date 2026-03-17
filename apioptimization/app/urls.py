from django.urls import path
from .views import UserDetailV1, UserDetailV2, UserList, UserDetailV3, UserDetailV4
    
urlpatterns = [ 
    path('users/', UserList.as_view(), name='user-list'),
    path('users/v1/<int:pk>/', UserDetailV1.as_view(), name='user-detail-v1'),  #Time taken: 17 second
    path('users/v2/<int:pk>/', UserDetailV2.as_view(), name='user-detail-v2'),  # Time taken: 8 second
    path('users/v3/<int:pk>/', UserDetailV3.as_view(), name='user-detail-v3'),  # Time taken: 1.5 to 2 second
    path('users/v4/<int:pk>/', UserDetailV4.as_view(), name='user-detail-v4'),  # Time taken: 0.5 second
]
