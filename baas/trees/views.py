# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.contrib.auth.models import Group, User

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden

from django.template import RequestContext

from django.utils.decorators import method_decorator

from django.template.defaultfilters import slugify

from .models import Tree, Study
from .forms import CreateStudyForm, AddTreeForm

from guardian.shortcuts import assign_perm, get_objects_for_user
from guardian.decorators import permission_required_or_403


class AddTreeFileView(PermissionRequiredMixin, UpdateView):
    # Require permission to add trees, if not it raises an exception
    permission_required = 'trees.add_tree'
    raise_exception = True

    template_name = 'trees/tree_form.html'

    def get(self, request):
        return render_to_response(self.template_name,
                                  {'form_tree': AddTreeForm(),
                                   'form_study': CreateStudyForm()},
                                  context_instance=RequestContext(request))

    def post(self, request):
        form_study = CreateStudyForm(request.POST)
        form_tree = AddTreeForm(request.POST)

        if not form_study.is_valid():
            m = 'You should pick a new name for the study.'
            messages.add_message(request, messages.ERROR, m)
            return HttpResponseRedirect(reverse('trees:add'))

        new_slug = slugify(form_study.cleaned_data['name'])

        if Study.objects.filter(slug=new_slug):
            m = 'This name is already taken, pick a different one.'
            messages.add_message(request, messages.ERROR, m)
            return HttpResponseRedirect(reverse('trees:add'))

        if not form_tree.is_valid():
            m = 'Something is wrong with the Tree, it is not a valid JSON format!'
            messages.add_message(request, messages.ERROR, m)
            return HttpResponseRedirect(reverse('trees:add'))

        study = form_study.save()

        tree = form_tree.save(commit=False)
        tree.created_by = request.user.username
        tree.study = study
        tree.version = 1
        tree.save()

        self.create_group(study.slug, request.user, study)

        return HttpResponseRedirect(reverse('trees:detail',
                                            kwargs={'study_slug': study.slug,
                                                    'version': tree.version})
                                    )

    def create_group(self, name, user, study):
        # Create a new group with name of the study and add the user that adds it to db
        new_group = Group(name=name)
        new_group.save()
        user.groups.add(new_group)

        # Add permission to hange this tree to that specific group
        assign_perm('trees.change_study', new_group, study)


class StudyListView(LoginRequiredMixin, ListView):
    model = Study

    def get_queryset(self):
        """Return the trees a user should be able to access."""
        allowed_objects = get_objects_for_user(user=self.request.user, perms='trees.change_study')
        return allowed_objects.order_by('name')


class TreeDetailView(LoginRequiredMixin, DetailView):
    model = Tree
    # These next two lines tell the view to index lookups by username
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self):
        study_slug = self.kwargs['study_slug']
        version = self.kwargs['version']
        return self.model.objects.get(study__slug=study_slug, version=version)

    @permission_required_or_403('trees.change_study', (Study, 'slug', 'study_slug'))
    def dispatch(self, *args, **kwargs):
        return super(TreeDetailView, self).dispatch(*args, **kwargs)

    @property
    def user(self):
        return self.request.user


class StudyDetailListView(LoginRequiredMixin, ListView):
    model = Study
    template_name_suffix = '_detail_list'

    @permission_required_or_403('trees.change_study', (Study, 'slug', 'study_slug'))
    def dispatch(self, *args, **kwargs):
        return super(StudyDetailListView, self).dispatch(*args, **kwargs)

    def versions(self):
        study_slug = self.kwargs['study_slug']
        return Tree.objects.filter(study__slug=study_slug).order_by('-save_date')

    def editors(self):
        """Return the last five published questions."""
        study_slug = self.kwargs['study_slug']
        g = Group.objects.get(name=study_slug)
        return g.user_set.all()

    @property
    def study(self):
        return self.model.objects.get(slug=self.kwargs['study_slug'])

    @property
    def user(self):
        return self.request.user


class EditTree(LoginRequiredMixin, TemplateView):
    model = Tree
    template_name = 'trees/tree_edit.html'

    def json_tree(self):
        return json.dumps(self.tree.json)

    @property
    def version(self):
        return self.kwargs['version']

    # This decorator makes sure the view checks for object
    @method_decorator(permission_required_or_403('trees.change_study',
                                                 (Study, 'slug', 'study_slug'),
                                                 accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(EditTree, self).dispatch(*args, **kwargs)

    @property
    def tree(self):
        return self.model.objects.get(study__slug=self.kwargs['study_slug'], version=self.version)


class AddTreeVersionView(UpdateView):
    template_name = 'trees/tree_form.html'
    model = Tree

    @permission_required_or_403('trees.change_study', (Study, 'slug', 'study_slug'))
    def dispatch(self, *args, **kwargs):
        return super(AddTreeVersionView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = AddTreeForm(request.POST)

        if form.is_valid():
            tree = form.save(commit=False)

            tree.created_by = request.user.username
            tree.version = self.highest_version() + 1
            tree.study = self.study

            tree.save()

            return HttpResponseRedirect(reverse('trees:detail_list',
                                                kwargs={'study_slug': self.study.slug})
                                        )
        else:
            # TODO add alert that form is invalid
            return HttpResponseForbidden()

    def highest_version(self):
        trees = self.model.objects.filter(study__slug=self.kwargs['study_slug'])
        return max([t.version for t in trees])

    @property
    def version(self):
        return self.kwargs['version']

    @property
    def study(self):
        return Study.objects.get(slug=self.kwargs['study_slug'])

    @property
    def user(self):
        return self.request.user
