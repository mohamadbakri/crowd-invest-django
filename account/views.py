from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from project.models import ProjectDonator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.urls import reverse
from .token import generate_token
import threading


from .models import Profile
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .authentication import *


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            ######
            if user and user.username != 'admin' and not user.profile.is_email_verified:
                messages.add_message(request, messages.ERROR,
                                     'Email is not verified, please check your email inbox')
                return render(request, 'account/login.html', {"form": form}, status=401)

            if not user:
                messages.add_message(request, messages.ERROR,
                                     'Invalid credentials, try again')
                return render(request, 'account/login.html', {"form": form}, status=401)

            login(request, user)

            # messages.add_message(request, messages.SUCCESS,
            #                      f'Welcome {user.first_name, " ", user.last_name}')
            return redirect(reverse('home'))

    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


def user_logout(request):
    form = LoginForm()
    logout(request)
    # messages.info(request, "You have successfully logged out.")
    return render(request, 'account/login.html', {"form": form})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileEditForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(
                user_form.cleaned_data['password'])
            # Save the User object
            new_user.username = user_form.cleaned_data['first_name'].capitalize(
            )
            new_user.is_staff = True
            # new_user.is_superuser = True
            new_user.save()
            # Create the user profile
            profile_form = ProfileEditForm(
                instance=new_user.profile,
                data=request.POST,
                files=request.FILES)
            profile_form.save()
            # # Send Activation Email
            send_activation_email(new_user, request)
            messages.add_message(request, messages.SUCCESS,
                                 'We sent you an email to verify your account')
            # Send Activation Email

            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user,
                           'profile_form': ProfileEditForm,
                           })
    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileEditForm()
    return render(request, 'account/register.html',
                  {'user_form': user_form, 'profile_form': profile_form,
                   })


@ login_required
def show_profile(request):
    user_donations_per_project = []
    project_collected_donations = []
    user = request.user
    profile = user.profile

    # Calculate total project investment till target(what campaign colledted till target)
    for p in user.campaigns.all():
        project_collected_donations.append((p,
                                            round(ProjectDonator.objects.filter(
                                                project_id=p.id).aggregate(Sum('donation_value')).get('donation_value__sum', 0) or 0)
                                            ))

    # Map donator investment per project

    for donation in user.donations.through.objects.filter(donator__email=user.email):
        user_donations_per_project.append(
            (donation.project.title, round(donation.donation_value)))

    # Calculate user total investment in all projects

    user_total_donations = ProjectDonator.objects.filter(
        donator__email=user.email).aggregate(Sum('donation_value')).get('donation_value__sum', 0)

    return render(request,
                  'account/show_profile.html',
                  {'user': user,
                   'user_donations_per_project': user_donations_per_project,
                   'user_total_donations': round(user_total_donations or 0),
                   'project_collected_donations': project_collected_donations,
                   'profile': profile})


@ login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # messages.success(request, 'Profile updated successfully')
            return redirect('profile_show')
        else:
            pass
            # messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        user_form.fields['email'].widget.attrs['readonly'] = True
    return render(request,
                  'account/edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   })


@login_required
def delete_profile(request):
    user = User.objects.get(pk=request.user.id)
    if request.method == 'POST':
        user.delete()
        user_logout(request)
        return render(request,
                      'account/delete_done.html')
        # return redirect('home')
    return render(request,
                  'account/delete.html',
                  {'user': user})


# def _redirect(request, url):
#     # nxt = 'home'
#     nxt = request.GET.get("next", None)
#     if nxt:
#         return redirect(nxt)
#     else:
#         return redirect(url)


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


def send_activation_email(user, request):
    current_site = get_current_site(request)
    email_subject = 'Activate your account'
    email_body = render_to_string('account/activate.html', {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })

    email = EmailMessage(subject=email_subject, body=email_body,
                         from_email=settings.DEFAULT_FROM_EMAIL,
                         #  from_email=settings.EMAIL_FROM_USER,
                         to=[user.email]
                         )

    if not settings.TESTING:
        EmailThread(email).start()


def activate_user(request, uidb64, token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception as e:
        user = None

    if user and generate_token.check_token(user, token):
        user.profile.is_email_verified = True
        user.profile.save()

        messages.add_message(request, messages.SUCCESS,
                             'Email verified, you can now login')
        return redirect(reverse('login'))

    return render(request, 'authentication/activate-failed.html', {"user": user})
