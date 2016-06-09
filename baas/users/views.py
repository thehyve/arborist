# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, View

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from guardian.shortcuts import get_users_with_perms

from .models import User, Group
from ..trees.models import Tree, Study


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):

    fields = ['name', ]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'


class AddToGroupView(PermissionRequiredMixin, ListView):
    # Require permission to add trees, if not it raises an exception
    permission_required = 'trees.add_tree'
    raise_exception = True

    template_name_suffix = '_add_to_group'

    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'

    @property
    def study(self):
        return Study.objects.get(slug=self.kwargs['study_slug'])

    @property
    def has_access(self):
        return get_users_with_perms(self.study)


class UpdateGroupView(PermissionRequiredMixin, View):
    permission_required = 'trees.add_tree'
    raise_exception = True

    def get(self, request, **kwargs):
        slug = kwargs.get('study_slug')

        # find group for this study and add the user.
        group = Group.objects.get(name=slug)
        username = kwargs.get('username')
        user = User.objects.get(username=username)
        user.groups.add(group)

        return HttpResponseRedirect(reverse('trees:detail_list',
                                    kwargs={'study_slug': slug}))




