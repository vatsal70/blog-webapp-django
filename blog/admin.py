from django.contrib import admin

# Register your models here.
from .models import Post, Contact, Category, Search, User


admin.site.register(User)
admin.site.register(Post)
admin.site.register(Contact)
admin.site.register(Category)
admin.site.register(Search)