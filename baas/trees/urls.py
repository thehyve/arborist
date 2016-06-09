# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    # URL pattern for the AddTreeFile
    url(
        regex=r'^$',
        view=views.StudyListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^add/$',
        view=views.AddTreeFileView.as_view(),
        name='add'
    ),
    url(
        regex=r'^(?P<study_slug>[\w.@+-]+)/(?P<version>[\d.-]+)/~edit/$',
        view=views.EditTree.as_view(),
        name='edit'
    ),
    url(
        regex=r'^(?P<study_slug>[\w.@+-]+)/(?P<version>[\d.-]+)/$',
        view=views.TreeDetailView.as_view(),
        name='detail'
    ),
    url(
        regex=r'^(?P<study_slug>[\w.@+-]+)/$',
        view=views.StudyDetailListView.as_view(),
        name='detail_list'
    ),
    url(
        regex=r'^(?P<study_slug>[\w.@+-]+)/~version/$',
        view=views.AddTreeVersionView.as_view(),
        name='version'
    ),
]
