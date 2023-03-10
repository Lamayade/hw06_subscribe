from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Новый текст',
            'group': 'Группа записи',
            'image': 'Картинка',
        }
        help_texts = {
            'text': 'Напишите текст записи',
            'group': 'Выберите группу',
            'image': 'Прикрепите картинку',
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Новый комментарий',
        }
        help_texts = {
            'text': 'Напишите текст комментария',
        }
