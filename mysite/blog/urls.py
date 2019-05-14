from django.contrib import admin
from django.urls import path
from django.urls import include, re_path
from blog import views

app_name = 'blog'
urlpatterns = [
    re_path(r'(?P<id>\d+)/post_edit/$',views.post_edit,name="post_edit"),
    re_path(r'(?P<id>\d+)/post_delete/$', views.post_delete, name="post_delete"),
    re_path(r'(?P<id>\d+)/favourite_post/$', views.favourite_post, name="favourite_post"),
    re_path(r'(?P<id>\d+)/(?P<slug>[\w-]+)/$',views.post_detail,name='post_detail'),
    path('create/',views.post_create,name='post_create'),
    path('edit_profile/', views.edit_profile, name="edit_profile"),
    path('favourites/', views.post_favourite_list, name="post_favourite_list"),
    # re_path(r'^profile/(?P<pk>\d+)/$', views.view_profile, name='view_profile_with_pk'),

    # re_path(r'(?P<id>\d+)/post_edit/$',views.PostUpdateView.as_view(),name='post_edit'),
]
