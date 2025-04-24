from django import forms
from django.contrib.auth.models import User
from .models import Topic, Post, Tag

class TopicForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Topic
        fields = ['title', 'content', 'pinned', 'tags']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']

class ManageAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
