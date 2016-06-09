# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    # URL pattern for the UserListView
    url(
        regex=r'^$',
        view=views.UserListView.as_view(),
        name='list'
    ),

    # URL pattern for the UserRedirectView
    url(
        regex=r'^~redirect/$',
        view=views.UserRedirectView.as_view(),
        name='redirect'
    ),

    # URL pattern for the UserDetailView
    url(
        regex=r'^(?P<username>[\w.@+-]+)/$',
        view=views.UserDetailView.as_view(),
        name='detail'
    ),

    # URL pattern for the UserUpdateView
    url(
        regex=r'^~update/$',
        view=views.UserUpdateView.as_view(),
        name='update'
    ),
    # URL pattern for the UserUpdateView
    url(
        regex=r'^add-to-group/(?P<study_slug>[\w.@+-]+)/$',
        view=views.AddToGroupView.as_view(),
        name='add_to_group'
    ),
    # URL pattern for the UserUpdateView
    url(
        regex=r'^update-group/(?P<study_slug>[\w.@+-]+)/(?P<username>[\w.@+-]+)/$',
        view=views.UpdateGroupView.as_view(),
        name='update_group'
    ),
]
