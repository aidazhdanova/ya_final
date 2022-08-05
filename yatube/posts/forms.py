from django.forms import ModelForm
from .models import Post
from .models import Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = [
            'group',
            'text',
            'image',
        ]
        labels = {
            'group': 'Выберите группу',
            'text': 'Текст поста',
            'image': 'Изображение'
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': 'Текст поста',
        }
