from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
# from . models import Contact, Post, BlogComment, Series, Subscriber
from . models import Contact
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
# from blog.templatetags import extras
from django.template.loader import render_to_string, get_template
from django.template import Context
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from . tokens import generate_token

# Create your views here.

def home(request):
    return render(request, 'exam/home.html')


def contact(request):
    # messages.success(request, 'Get in touch with me!!')
    if request.method=='POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        content = request.POST['content']
        
        if name=='':
            messages.error(request, "You must enter your name!!")
        elif email=='':
            messages.error(request, "Please enter your email!!")
        elif phone=='':
            messages.error(request, "Please enter your phone number!!")
        elif content=='':
            messages.error(request, "Please enter your message!!")
        else:
            contact = Contact(name=name, email=email, phone=phone, content=content)
            contact.save()
            messages.success(request, "Your message has been conveyed!!")
            
            subject = "Contact from TESTIFY!!"
            message = contact.name + " " + contact.email + " says " + contact.content
            from_email = settings.EMAIL_HOST_USER
            to_list = ["anubhavmadhav20@gmail.com", "201851024@iiitvadodara.ac.in","testify.iiitv@gmail.com"]
            
            send_mail(subject, message, from_email, to_list, fail_silently=True)
            
            subject2 = "Message from TESTIFY!!"
            message2 = "Hello " + contact.name + ". " + " Your message has been conveyed to TESTIFY. They will try to respond as soon as possible."
            from_email2 = settings.EMAIL_HOST_USER
            to_list2 = [contact.email]
            
            send_mail(subject2, message2, from_email2, to_list2, fail_silently=True)
            
            
    return render(request, 'exam/contact.html')


def handleSignup(request):
    if request.method == 'POST':
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        # Check for errorneous inputs
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username Already Exists. Try another username.")
            return redirect('Home')


        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('Home')
        
        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('Home')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('Home')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('Home')
        
        # Check if username already exists
        
        
        # Check if email already exists
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()
        messages.success(request, "Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account.")
        
       
        # Welcome Email
        subject = "Welcome to TESTIFY!!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to TESTIFY!! \nThank you for visiting our website.\nWe have also sent you a confirmation email, please confirm your email address. \n\nThanking You\nAnubhav Madhav"        
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        
        send_mail(subject, message, from_email, to_list, fail_silently=True)
      
      
      
        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email @ TESTIFY!!"
        message2 = render_to_string('email_confirmation.html',{
            
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
        email_subject,
        message2,
        settings.EMAIL_HOST_USER,
        [myuser.email],
        )
        email.fail_silently = True
        email.send()
        
        
        
        # template = render_to_string('email_confirmation.html', {'name': myuser.first_name })
        
        # email = EmailMessage(
        #     'Confirm your Email @ AM-Blogs!!',
        #     template,
        #     settings.EMAIL_HOST_USER,
        #     [myuser.email],
            
        # )
        # email.fail_silently = True
        # email.send()
        
        
        # name = myuser.first_name
        
        # send_mail(
        # 'Confirm your Email @ AM-Blogs!!',
        # get_template('email_confirmation.html').render(
        # Context({
        #    'name': name,
        # })
        # ),
        # settings.EMAIL_HOST_USER,
        # [myuser.email],
        # fail_silently = True
        # )
        
        
        
        
        return redirect('Home')
        
    else:
        return HttpResponse("404- Not Found")
    
    
    
def handleLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            messages.success(request, "Logged In Sucessfully!!")
            return redirect('Home')
        else:
            messages.error(request, "Bad Credentials!!")
            return redirect('Home')

    return HttpResponse("404")          # if request method is not 'post'


def handleLogout(request):
    logout(request)
    # messages.success(request, "Logged Out Successfully!!")
    return redirect('Home')
    
    # return HttpResponse("Logged Out")
    
    
    
def activate(request,uidb64,token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('Home')
    else:
        return render(request,'activation_failed.html')