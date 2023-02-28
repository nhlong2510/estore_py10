from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('login/', views.signup_login, name='login'),
    path('login2/', views.signup_login2, name='login2'),
    path('logout/', views.user_logout, name='logout'),
    path('logout2/', views.user_logout2, name='logout2'),
    path('my-account/', views.myaccount, name="my-account")
]
