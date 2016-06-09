# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from jsonfield import JSONField


class Study(models.Model):
    name = models.CharField(_('Name of Study'), max_length=50, blank=False)
    slug = models.SlugField(_('slug'), max_length=50, unique=True)

    def special_tree_add(self, *args, **kwargs):
        self.trees.add(
            tree=Tree(project=self, *args, **kwargs)
        )

    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.slug = slugify(self.name)
        super(Study, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('trees:detail_list', kwargs={'name': str(self)})


@python_2_unicode_compatible
class Tree(models.Model):
    version = models.IntegerField(_('Version'), blank=False)
    created_by = models.CharField(_('Created by'), blank=True, max_length=255)
    save_date = models.DateTimeField(auto_now_add=True)
    json = JSONField('Enter a valid Treefile JSON:')
    study = models.ForeignKey("trees.Study", related_name="trees")

    def __str__(self):
        return '{} version {}'.format(self.study.name, self.version)

    def get_absolute_url(self):
        return reverse('trees:detail', kwargs={'study_slug': self.study.slug,
                                               'version': self.version})

