from django.shortcuts import render, get_object_or_404
from django.shortcuts import HttpResponse, redirect
from .models import Post, Contact, Category, Search
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import PostForm, EditForm, AddCategory
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, CreateView, ListView, UpdateView, DeleteView
from ckeditor.fields import RichTextField
import requests
from bs4 import BeautifulSoup
from requests.compat import quote_plus
from . import models
import math
import json
import _pickle as pickle
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from .task import *


BASE_CRAIGSLIST_URL = 'https://losangeles.craigslist.org/search/?query={}'
BASE_IMAGE_URL = 'https://images.craigslist.org/{}_300x300.jpg'
BASE_NEW_URL = 'https://codewithharry.com/search/?query={}'
BASE_LINK_URL = 'https://codewithharry.com{}'





from io import BytesIO
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa

data = {
	"company": "Dennnis Ivanov Company",
	"address": "123 Street name",
	"city": "Vancouver",
	"state": "WA",
	"zipcode": "98663",


	"phone": "555-555-2345",
	"email": "youremail@dennisivy.com",
	"website": "dennisivy.com",
	}



def demo_view(request):
    # sleepy(10)
    # mail = ['vatsalvohera70@gmail.com', 'vatsalvohera255@gmail.com', 'vatsal.180670107120@gmail.com']
    # send_mail_task.delay(mail)
    return render(request, 'blog/demo.html', data)


def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None




#Opens up page as PDF
class ViewPDF(View):
	def get(self, request, *args, **kwargs):

		pdf = render_to_pdf('blog/demo.html', data)
		return HttpResponse(pdf, content_type='application/pdf')


#Automaticly downloads to PDF file
class DownloadPDF(View):
	def get(self, request, *args, **kwargs):
		
		pdf = render_to_pdf('blog/demo.html', data)

		response = HttpResponse(pdf, content_type='application/pdf')
		filename = "Invoice_%s.pdf" %("12341231")
		content = "attachment; filename='%s'" %(filename)
		response['Content-Disposition'] = content
		return response
# Create your views here.
def home(request):
    return render(request, 'blog/home.html')

def addCat(request):
    return render (request, 'blog/addcat.html')


class HomeView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = ['-post_id']
    context_object_name = "Posts" 
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        blg = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(blg, self.paginate_by)
        try:
            blg = paginator.page(page)
        except PageNotAnInteger:
            blg = paginator.page(1)
        except EmptyPage:
            blg = paginator.page(paginator.num_pages)
        context["Posts"] = blg
        return context


def catmenu(request):
    cat_menu_list = Category.objects.all()
    return render(request, 'blog/catmenu.html', {'cat_menu_list': cat_menu_list})

def LikeView(request, pk):
    post = get_object_or_404(Post, post_id=request.POST.get('like_id'))
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return HttpResponseRedirect(reverse('blogPost', args=[str(pk)]))

class BlogDetailView(DetailView):
    model = Post
    template_name = 'blog/blogpost.html'


    def get_context_data(self, *args, **kwargs):
        context = super(BlogDetailView, self).get_context_data(*args, **kwargs)
        stuff = get_object_or_404(Post, post_id=self.kwargs['pk'])
        total_likes = stuff.total_likes()
        liked = False
        if stuff.likes.filter(id=self.request.user.id).exists():
            liked = True

        context["total_likes"] = total_likes
        context["liked"] = liked
        return context


class AddBlog(SuccessMessageMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/addblog.html'
    success_message = 'Your Blog has been added successfully.'
    
    
class AddCat(SuccessMessageMixin, CreateView):
    model = Category
    form_class = AddCategory
    template_name = 'blog/addcat.html'
    success_message = 'Your Category has been added successfully.'


class UpdateBlog(SuccessMessageMixin, UpdateView):
    model = Post
    template_name = 'blog/edit.html'
    form_class = EditForm
    success_url = reverse_lazy('blogHome')
    success_message = 'Your Blog has been updated successfully.'



class DeleteBlog(SuccessMessageMixin, DeleteView):
    model = Post
    template_name = 'blog/delete.html'
    success_url = reverse_lazy('blogHome')
    success_message = 'Your Blog has been deleted successfully.'

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        data_to_return = super(DeleteBlog, self).delete(request, *args, **kwargs)
        messages.success(self.request, self.success_message % obj.__dict__)
        return data_to_return



def contact(request):
    print("Id", request.user.id)
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        que = True
        return render(request, 'blog/contact.html', {'que': que})
    return render(request, 'blog/contact.html')

def search(request):
    query = request.GET['query']
    if len(query) > 90:
        allposts = Post.objects.none()
    else:
        allposts1 = Post.objects.filter(title__icontains=query)
        allposts2 = Post.objects.filter(category__icontains=query)
        allposts = allposts1.union(allposts2)


    if allposts.count() == 0:
        messages.warning(request, 'Sorry User! Please try again.')

    params = {'allposts': allposts, 'query': query}
    return render(request, 'blog/search.html', params)

def CategoryView(request, cats):
    category_posts = Post.objects.filter(category=cats.replace('-', ' '))
    return render(request, 'blog/categories.html', {'cats': cats.title().replace('-', ' '), 'category_posts': category_posts})



# Stuff for web scrapping
def web_scrapper(request):
    print("In")
    return render(request, 'blog/web_scrap.html')


def web_results(request):
    print("Initiating.....")
    search = request.POST.get('search')
    print(search)
    models.Search.objects.create(search=search)
    final_url = BASE_CRAIGSLIST_URL.format(quote_plus(search))
    response = requests.get(final_url)
    data = response.text
    soup = BeautifulSoup(data, features='html.parser')

    post_listings = soup.find_all('li', {'class': 'result-row'})

    final_postings = []

    for post in post_listings:
        post_title = post.find(class_='result-title').text
        post_url = post.find('a').get('href')

        if post.find(class_='result-price'):
            post_price = post.find(class_='result-price').text
        else:
            post_price = 'N/A'

        if post.find(class_='result-image').get('data-ids'):
            post_image_id = post.find(class_='result-image').get('data-ids').split(',')[0].split(':')[1]
            post_image_url = BASE_IMAGE_URL.format(post_image_id)
        else:
            post_image_url = 'https://craigslist.org/images/peace.jpg'

        final_postings.append((post_title, post_url, post_price, post_image_url))
    stuff_for_frontend = {
        'search': search,
        'final_postings': final_postings, 
    }

    return render(request, 'blog/web_results.html', stuff_for_frontend)


def course_scrap(request):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", 
               "Accept-Encoding":"gzip, deflate", 
               "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
               "DNT":"1","Connection":"close", 
               "Upgrade-Insecure-Requests":"1"
               }
    # Get the input from the frontened to the backened.
    search_item = request.POST.get('search_item')
    print(search_item)
    
    
    # Initializing the num variable and an empty list.
    num = 0
    final_items = []
    
    
    # Get the url request to extract the number of results for the query.
    rr = requests.get(f'https://codewithharry.com/search/?query={quote_plus(search_item)}', headers=headers)
    data = rr.text
    soupp = BeautifulSoup(data, features="html.parser")
    num_srch = soupp.find('h1').text
    
    
    # Function to split the text from H1 tag and store in the list.
    def Convert(string): 
        li = list(string.split(" ")) 
        return li
    numsrch = Convert(num_srch)
    
    # Extracting the 
    if len(search_item) > 3:
        result_num = numsrch[35]
        result_num = result_num.replace('(', '')
        number_of_results = int(result_num)
        result_num = int(result_num)
        result_num = result_num / 10
        result_num = math.ceil(result_num)
        warning_error = ""
    else:
        result_num = 1
        print(len(search_item))
        warning_error = "Your length of query should be greater than 3. "
    end_page = result_num + 1
    for i in range(1, end_page):
        r = requests.get(f'https://codewithharry.com/search/?query={quote_plus(search_item)}&number={i}', headers=headers)
        content = r.content
        soup = BeautifulSoup(content, features="html.parser")
        items = soup.find_all('h2')
        for item in items:
            link_text = item.find('a').text
            url = item.find('a').get('href')
            link_url = f'https://codewithharry.com{url}'
            num = num + 1
            final_items.append((link_text, link_url, num))
    
    paginator = Paginator(final_items, 10)
    page = request.GET.get('page')
    try:
        user = paginator.page(page)
    except PageNotAnInteger:
        user = paginator.page(1)
    except EmptyPage:
        user = paginator.page(paginator.num_pages)
    print(len(final_items))
    if len(final_items) == 0:
        error_call = "We could not find your query."
    else:
        error_call = ""
    stuff = {
        'search_item': search_item,
        'final_items': final_items,
        'user': user,
        'warning_error': warning_error,
        'error_call': error_call,
        'number_of_results': number_of_results,
    }
    
    with open('file.txt', 'wb') as file:
        file.write(pickle.dumps(stuff))
    global item_search
    global item_final
    global user_item
    global error_msg
    global error_for_call
    global result_number
    
    def item_search():
        return search_item
    def item_final():
        return final_items
    def user_item():
        return user
    def error_msg():
        return warning_error
    def error_for_call():
        return error_call
    def result_number():
        return number_of_results
    return HttpResponseRedirect('/blog/new/')

def new_page(request):
    itemSearch = item_search()
    itemFinal= item_final()
    empty_list = error_for_call()
    paginator = Paginator(itemFinal, 10)
    page = request.GET.get('page')
    try:
        new_user = paginator.page(page)
    except PageNotAnInteger:
        new_user = paginator.page(1)
    except EmptyPage:
        new_user = paginator.page(paginator.num_pages)
    print(paginator.num_pages)
    
    stuffForFrontEnd = {
                         'item_search': itemSearch,
                         'item_final': itemFinal,
                         'user_item': new_user,
                         'error_msg': error_msg(),
                         'empty_list': empty_list,
                         'result_number': result_number(),
                         }
    return render(request, 'blog/new.html', stuffForFrontEnd)