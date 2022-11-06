from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, Count
from django.utils import timezone
from taggit.models import Tag


from .models import Project, ProjectDonator, CampaignImages, Rating, CampaignReport
from .forms import ImagesForm, ProjectForm
# Create your views here.

# https://solutionschecker.com/questions/how-to-upload-multiple-images-to-a-blog-post-in-django/
# Create your views here.


def home(request):
    projects = Project.objects.all()
    latest_5_projects = Project.objects.all().order_by('-publish_date')[:5]
    latest_5_featured_projects = Project.objects.all().filter(
        is_featured=True).order_by('-publish_date')[:5]

    RATED_5_PROJECTS = []
    for p in projects:
        project_collected_donations = round(ProjectDonator.objects.filter(
            project_id=p.id).aggregate(Sum('donation_value')).get('donation_value__sum', 0) or 0)

        project_available_for_funds = int(
            p.target or 0)-int(project_collected_donations or 0)

        if project_available_for_funds:
            RATED_5_PROJECTS.append([p, project_collected_donations,
                                    Rating.objects.filter(project=p).aggregate(
                                        Sum("rating"))["rating__sum"] or 0,
                                    project_available_for_funds]
                                    )

    RATED_5_PROJECTS.sort(key=lambda x: int(x[2]))

    categories = []
    for cat in Project.CATEGORIES:
        categories.append(cat[1])

    tags = Project.tags.all()

    context = {
        'tags': tags,
        'categories': categories,
        'latest_5_projects': latest_5_projects,
        'top_5_rated_projects': RATED_5_PROJECTS[:5],
        "featured_projects": latest_5_featured_projects,
    }
    return render(request, 'project/home.html', context)


def campaigns(request):
    projects_statues = []
    data = []
    slug = None
    category = request.GET.get('category')
    cat = [item[0] for item in Project.CATEGORIES
           if item[1] == category]
    # images = Project.objects.get(id=8).campaigns.all()
    if category == None:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(category=cat[0])

    slug = request.GET.get('slug')
    if slug:
        tag = get_object_or_404(Tag, slug=slug)
        # Filter posts by tag name
        projects = Project.objects.filter(tags=tag)

    # Pagination with 3 posts per page
    paginator = Paginator(projects, 3)
    page_number = request.GET.get('page')
    # page_number = request.GET.get('page', 1)
    try:
        projects = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer deliver the first page
        projects = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range deliver last page of results
        projects = paginator.page(paginator.num_pages)

    # for p in projects:
    #     data.append(tuple((p.gallary.all()[0].images.url, p)))

    if projects:
        for p in projects:
            project_collected_donations = ProjectDonator.objects.filter(
                project_id=p.id).aggregate(Sum('donation_value')).get('donation_value__sum', 0)
            project_available_for_funds = int(
                p.target or 0)-int(project_collected_donations or 0)
            percentage = int(project_collected_donations or 0) / \
                int(p.target or "Not yet.")*100
            data.append([p.gallary.all()[0].images.url, p,
                         round(project_collected_donations or 0), project_available_for_funds, percentage])

    context = {
        'projects': projects,
        'page': page_number,
        'categories': Project.CATEGORIES,
        'projects_statues': projects_statues,
        'data': data,
    }
    return render(request, 'project/projects.html',  context)


def search_campaigns(request):
    data = []
    slug = request.POST.get('tag', False)
    title = request.POST.get('title', False)
    if slug:
        tag = get_object_or_404(Tag, slug=slug)
        projects = Project.objects.filter(
            title__contains=title).filter(tags=tag)
    else:
        projects = Project.objects.filter(
            title__contains=title)

    # Pagination with 3 posts per page
    paginator = Paginator(projects, 3)
    page_number = request.GET.get('page')
    # page_number = request.GET.get('page', 1)
    try:
        projects = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer deliver the first page
        projects = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range deliver last page of results
        projects = paginator.page(paginator.num_pages)

    # for p in projects:
    #     data.append(tuple((p.gallary.all()[0].images.url, p)))

    if projects:
        for p in projects:
            project_collected_donations = ProjectDonator.objects.filter(
                project_id=p.id).aggregate(Sum('donation_value')).get('donation_value__sum', 0)
            project_available_for_funds = int(
                p.target or 0)-int(project_collected_donations or 0)
            percentage = int(project_collected_donations or 0) / \
                int(p.target or "Not yet.")*100
            data.append([p.gallary.all()[0].images.url, p,
                         round(project_collected_donations or 0), project_available_for_funds, percentage])

    context = {
        'projects': projects,
        'page': page_number,
        'categories': Project.CATEGORIES,
        "data": data,
    }
    return render(request, 'project/projects.html',  context)
################################
#################################


def single_campaign(request, project_id):
    project = Project.objects.get(id=project_id)

    project_collected_donations = ProjectDonator.objects.filter(
        project_id=project_id).aggregate(Sum('donation_value')).get('donation_value__sum', 0)

    project_available_for_funds = int(
        project.target or 0)-int(project_collected_donations or 0)

    # prcentage of collected to target
    percentage = int(project_collected_donations or 0) / \
        int(project.target or "Not yet.")

    # Rating
    # rating = Rating.objects.filter(project=project, user=request.user).first()
    if request.user.is_authenticated:
        rating = Rating.objects.filter(
            project=project, user=request.user).first()
        project.user_rating = rating.rating if rating else 0

    images = project.gallary.all()

    # similar_projects
    project_tags_ids = project.tags.values_list('id', flat=True)
    similar_projects = Project.objects.filter(
        tags__in=project_tags_ids).exclude(id=project.id)
    similar_projects = similar_projects.annotate(same_tags=Count(
        'tags')).order_by('-same_tags', '-publish_date')[:4]
    context = {
        'project': project,
        'user': request.user,
        'similar_projects': similar_projects,
        "images": images,
        'project_collected_donations': project_collected_donations,
        'project_available_for_funds': round(project_available_for_funds, 0),
        'percentage': round(percentage*100, 1),
    }
    return render(request, 'project/single_campaign.html',  context)


@ login_required
def create_campaign(request):
    ImageFormSet = modelformset_factory(
        CampaignImages,  form=ImagesForm, extra=5)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        formset = ImageFormSet(request.POST, request.FILES,
                               queryset=CampaignImages.objects.none())
        if form.is_valid() and formset.is_valid():
            newpost = form.save(commit=False)
            # useradmin = User.objects.get(username='admin')
            newpost.author = request.user
            newpost.save()
            # Without this next line the tags won't be saved.
            form.save_m2m()
            for form in formset.cleaned_data:
                # this helps to not crash if the user
                # do not upload all the photos
                if form:
                    image = form['images']
                    photo = CampaignImages(poroject=newpost, images=image)
                    photo.save()
            # use django messages framework
            # messages.success(request,"Yeeew, check it out on the home page!")
            return HttpResponseRedirect("/")

        context = {
            'categories': "",
            'formset': formset,
            'form': form,
        }
        return render(request, 'Project/create_project.html', context)
    else:
        formset = ImageFormSet(queryset=CampaignImages.objects.none())
        context = {
            'form': ProjectForm,
            'formset': formset,
        }
    return render(request, 'Project/create_project.html', context)


@ login_required
def delete_campaign(request, campaign_id):
    project = Project.objects.get(pk=campaign_id)
    if request.method == 'POST':
        project.delete()
        return render(request,
                      'project/delete_done.html')
    return render(request,
                  'project/delete.html',
                  {'user': request.user})


@ login_required
def invest(request, project_id):
    available = int(request.GET.get('v', False))
    project = get_object_or_404(Project, pk=project_id)
    images = project.gallary.all()
    context = {
        'categories': "",
        'project': project,
        "images": images,
        "amount": request.POST['amount']
    }
    if request.method == "POST":
        amount = request.POST.get('amount', False)

        # validate
        if int(amount) <= available:
            if amount and amount.isnumeric():
                if project.campaign_end_date > timezone.now():
                    apply_donation(project, request.user, amount)
                return redirect('single_campaign', project_id)

        else:
            messages.error(request, 'Amount exceeds available for investment')
            return render(request, 'project/re_invest.html', context)
            # return render(request, 'project/single_campaign.html', context)

    return render(request, 'project/single_campaign.html', context)


def apply_donation(project, user, amount):
    prev_donations = project.donators.through.objects.filter(
        donator_id=user.id).filter(project_id=project.id)

    # has donated for this campaign before
    if prev_donations:
        prev_donations[0].donation_value += float(amount)
        prev_donations[0].save()
    # first time
    else:
        ProjectDonator.objects.create(
            donation_value=amount, project_id=project.id, donator_id=user.id)


################################
#################################


@ login_required
def rate(request, project_id: int, rating: int):
    project = Project.objects.get(id=project_id)
    Rating.objects.filter(project=project, user=request.user).delete()
    project.rating_set.create(user=request.user, rating=rating)
    return single_campaign(request, project_id)


@ login_required
def report_campaign(request, campaign_id):

    if request.method == "POST":
        campaign = get_object_or_404(Project, pk=campaign_id)
        context = {"campaign": campaign}

        details = request.POST.get('details', '')
        subject = request.POST.get('subject', '')

        if details and subject and not is_spam(request.user.id, campaign_id):
            CampaignReport.objects.create(
                details=details, campaign_id=campaign_id, reporter_id=request.user.id)

    return redirect('single_campaign', campaign_id)


# user can report a cmapaign only two times(max reporting per project for user)

def is_spam(user, campaign):
    return (CampaignReport.objects.filter(reporter_id=user, campaign_id=campaign).count() >= 3)
