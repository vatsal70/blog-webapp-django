from django.db import models
from django.contrib import messages
# from django.contrib.auth.models import User
from django.utils.timezone import now
from django.conf import settings
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.db.models import Count
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime
from django.dispatch import receiver
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

# Create your models here.
class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, username, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        if not username:
            raise ValueError('The given username must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, username, **extra_fields)

    def create_superuser(self, email, username, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, username, password, **extra_fields)
    


class User(AbstractUser):
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(error_messages={'unique': 'A user with that username already exists.'}, verbose_name='username', max_length=15, unique=True, null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def get_absolute_url(self):
        return redirect('/')

class Category(models.Model):
    name = models.CharField(max_length=150, default=" ")


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('AddCat')

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        return super(Category, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Categories"

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    # category = models.CharField(max_length=150, default="")
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    sub_title = models.CharField(max_length=50)
    body = RichTextField(blank=True, null=True)
    # body = models.TextField(max_length=5000)
    pub_date = models.DateField(default=now())
    likes = models.ManyToManyField(User, related_name='blogpost')
    header_image = models.ImageField(blank = True, upload_to = "blog/images", default = "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DXDKlzbgFcG8&psig=AOvVaw3YCne2m5xc2ipBxTzQSlSn&ust=1604999979875000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCJC-_oCR9ewCFQAAAAAdAAAAABAD")

    def total_likes(self):
        return self.likes.count()


    def __str__(self):
        return self.title + ' | ' + str(self.author)

    def get_absolute_url(self):
        return reverse('blogHome')
    
    
    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        storage, path = self.header_image.storage, self.header_image.path
        # Delete the model before the file
        super(Post, self).delete(*args, **kwargs)
        # Delete the file after the model
        storage.delete(path)
    
    class Meta:
        verbose_name_plural = "Posts"


class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=70, default="")
    desc = models.CharField(max_length=500, default="")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Contacts"
    
class Search(models.Model):
    search = models.CharField(max_length=500, default=" ", null=True)
    created = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return '{}'.format(self.search)

    def get_absolute_url(self):
        return reverse('webResults')
    
    class Meta:
        verbose_name_plural = 'Searches'