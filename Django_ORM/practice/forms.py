from django import forms
from .models import Post, Comment, Image
from django.forms.models import inlineformset_factory

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {'content': forms.Textarea(attrs={'rows': 5})}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {'content': forms.Textarea(attrs={'rows': 2})}


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']

ImageFormSet = inlineformset_factory(Post, Image, form=ImageForm, extra=1)
