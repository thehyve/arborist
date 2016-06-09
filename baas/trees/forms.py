from django import forms

from .models import Tree, Study


class CreateStudyForm(forms.ModelForm):
    """
    A form that creates a associated project for a Treefile.
    """
    class Meta:
        model = Study
        fields = ["name", ]


class AddTreeForm(forms.ModelForm):
    """
    A form that creates a new version of a TreeFile
    """
    class Meta:
        model = Tree
        fields = ["json", ]
