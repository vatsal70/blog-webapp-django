from django import forms
from .models import Post, Category


choice_list = []
try:
    cat_choices = Category.objects.all().values_list('name', 'name')
    for item in cat_choices:
        print(item)
        choice_list.append(item)
except:
    print(choice_list)


class AddCategory(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Category'}),
        }
        
        
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'author', 'sub_title', 'body', 'category', 'header_image')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Title'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'User', 'value': '', 'id': 'auth', 'type':'hidden'}),
            # 'category': forms.Select(choices=choice_list, attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'sub_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Sub-Title'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Content'}),
        }


class EditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'sub_title', 'body', 'category', 'header_image')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Title'}),
            'sub_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Sub-Title'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Content'}),
            'category': forms.Select(choices=choice_list, attrs={'class': 'form-control'}),
        }