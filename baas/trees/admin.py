# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import Tree, Study

from guardian.admin import GuardedModelAdmin


class TreeAdmin(GuardedModelAdmin):
    study_name = Tree.study.field.name
    list_display = (study_name, 'version', 'created_by', 'save_date')
    search_fields = (study_name, 'created_by')
    ordering = ('-save_date',)
    date_hierarchy = 'save_date'


class StudyAdmin(GuardedModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("slug",)}


admin.site.register(Tree, TreeAdmin)
admin.site.register(Study, StudyAdmin)
