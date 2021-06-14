from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, PasswordResetForm
from django.urls import reverse_lazy
from .forms import SignUpForm, PasswordChangingForm, EditUserProfile
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from blog.models import *
from django.contrib import messages
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError

# Create your views here.


class PasswordsChangeView(SuccessMessageMixin, PasswordChangeView):
    form_class = PasswordChangingForm
    success_url = reverse_lazy('blogHome')
    success_message = 'Your password has been updated successfully.'


class UserRegisterView(SuccessMessageMixin, generic.CreateView):
    form_class = SignUpForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')
    success_message = 'Your profile has been created successfully. Kindly login to continue.'
    
    
    #auto login after register: 
    def form_valid(self, form):
        #save the new user first
        form.save()
        #get the username and password
        email = self.request.POST['email']
        password = self.request.POST['password1']
        print(email)
        print(password)
        #authenticate user then login
        user_exists = User.objects.filter(email=email).exists()
        if user_exists:
            try:
                user = authenticate(username=email, password=password)
                login(self.request, user)
                messages.info(self.request, f"You are now logged in as {email}")
                print("You are now logged in as", email)
            except:
                print("Incorrect Password")
        else:
            print("username does not exists.")
        return HttpResponseRedirect(reverse('blogHome'))

# class UserEditView(SuccessMessageMixin, generic.UpdateView):
#     form_class = EditProfile
#     template_name = 'registration/editprofile.html'
#     success_url = reverse_lazy('blogHome')
#     success_message = 'Your profile has been updated successfully.'
    
#     def get_object(self):
#         return self.request.user
    
def user_update_details(request):
    try:    
        user_obj= get_object_or_404(User, id = request.user.id)
        if request.method == 'POST':
            user_form = EditUserProfile(request.POST, instance = user_obj)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your Profile has been updated!')
                return redirect('blogHome')
        else:
            user_form = EditUserProfile(instance = user_obj)

        context={'form': user_form}
    except:
        print("Inside the except block of 'user_update_details'")
        context = {
            
        }
    return render(request, 'registration/editprofile.html', context )





def password_reset_request(request):
    if request.method == "POST": 
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            print("Data", data)
            associated_users = User.objects.filter(Q(email=data))
            print("AU", associated_users)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "registration/password_reset_email.txt"
                    print(user.email)
                    print(user.pk)
                    print(user)
                    c = {
                    "email":user.email,
                    'domain':'127.0.0.1:8000',
                    'site_name': 'Blog WebApp',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, settings.EMAIL_HOST_USER , [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect('/members/reset_password_sent')
            else:
                messages.success(request, "email id- %s does not exist." % data)
                
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="registration/password_reset.html", context={"password_reset_form":password_reset_form})
