from django.shortcuts import render, redirect, HttpResponse, get_object_or_404, Http404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  # Make sure to use the correct User model
from .forms import UserRegistrationForm
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .tokens import account_activation_token

def resend_activation(request):
    # This view handles resending activation email
    if request.method == 'GET':
        try:
            # Try to find a user with is_active=False
            # You might want to modify this logic based on how you want to identify users
            users = User.objects.filter(is_active=False)
            
            if not users.exists():
                messages.error(request, "No pending activations found.")
                return redirect('login')
            
            # If multiple inactive users, you might want to prompt for email
            # For simplicity, we'll use the first inactive user
            user = users.first()
            
            # Generate new activation details
            site = get_current_site(request)
            mail_subject = "Resend: Confirm your Kikapu account"
            
            context = {
                'user': user,
                'domain': site.domain,
                'uid': user.id,
                'token': account_activation_token.make_token(user)
            }
            
            # Render HTML content
            html_message = render_to_string('authentication/confirm-email.html', context)
            # Create plain text version
            text_message = strip_tags(html_message)

            # Create email
            from_email = settings.EMAIL_HOST_USER
            email = EmailMultiAlternatives(
                mail_subject,
                text_message,
                from_email,
                [user.email]
            )
            
            # Attach HTML content
            email.attach_alternative(html_message, "text/html")
            
            # Send email
            email.send(fail_silently=False)

            messages.success(request, "Activation email has been resent. Please check your inbox.")
            return redirect('login')
        
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('signup')
    
    # Fallback redirect
    return redirect('login')


def signup_view(request):       
    if request.method == 'POST':
        reg_form = UserRegistrationForm(request.POST)

        if reg_form.is_valid():
            instance = reg_form.save(commit=False)
            instance.is_active = False
            instance.save()

            site = get_current_site(request)
            mail_subject = "Confirm your Kikapu account"
            
            # Context for email template
            context = {
                'user': instance,
                'domain': site.domain,
                'uid': instance.id,
                'token': account_activation_token.make_token(instance)
            }
            
            # Render HTML content
            html_message = render_to_string('authentication/confirm-email.html', context)
            # Create plain text version
            text_message = strip_tags(html_message)

            # Create email
            to_email = reg_form.cleaned_data.get('email')
            from_email = settings.EMAIL_HOST_USER
            email = EmailMultiAlternatives(
                mail_subject,
                text_message,
                from_email,
                [to_email]
            )
            
            # Attach HTML content
            email.attach_alternative(html_message, "text/html")
            
            # Send email
            email.send(fail_silently=False)

            return redirect('signup-success')
                            
    else:
        reg_form = UserRegistrationForm()

    context = {
        'reg_form': reg_form,
    }

    return render(request, 'authentication/signup.html', context)

# Rest of your views remain unchanged
def signup_success_view(request):
    return render(request, 'authentication/signup-success.html')

def account_activate_view(request, uid, token):
    try:
        user = get_object_or_404(User, pk=uid)
    except:
        raise Http404("No User found")
    
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'authentication/activate-account.html')
    else:
        return HttpResponse("Invalid activation link. Please contact support.")

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            redirect_url = request.GET.get('next','home')
            return redirect(redirect_url)
        else:
            messages.error(request, f"Oops! Username or Password is invalid. Please try again.")

    return render(request, 'authentication/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')