from django import forms
from .models import Post, Comment, Image


class PostForm(forms.ModelForm):
    # images = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}), required=False) 
    class Meta:
        model = Post
        fields = ['writer', 'title', 'content']
        widgets = { 
            'content': forms.Textarea(attrs={'rows': 5}),
        }



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['writer', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2}),
        }
