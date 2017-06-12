import copy
from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Project, ProjectOverview,IosProject,IosRelease,AndroidProject,AndroidRelease, ProjectOverviewScreenshot
from wsgiref.util import FileWrapper
from django_user_agents.utils import get_user_agent
from .create_manifest import write_manifest_send
from operator import itemgetter

@login_required()
def home_page(request):
    request.session['platform'] = ''
    apps_to_display = []
    # Get all non-archived project objects.
    avail_apps = Project.objects.filter(is_archived=False)

    # Iterate through each project to set the apps which will be passed to the template.
    for app in avail_apps:
        one_app = {}
        one_app['title'] = app.title
        try:
            release = AndroidRelease.objects.filter(android_project__project_overview__project_id = app.id, is_archived=False, is_featured_release=True)\
                .order_by('-major_version','-minor_version','-point_version','-build_version')[0]
            one_app['platform'] = 'android'
            one_app['releaseDate'] = release.timestamp
            one_app['releaseVersion'] = '{0}.{1}.{2}.{3}'.format(release.major_version,release.minor_version,release.point_version,release.build_version)
            one_app['id'] = release.id
            one_app['description'] = release.android_project.project_overview.description
            one_app['icon'] = release.android_project.project_overview.icon
            apps_to_display.append(copy.copy(one_app))
        except IndexError or AndroidRelease.DoesNotExist:
            pass
        try:
            release = IosRelease.objects.filter(ios_project__project_overview__project_id = app.id, is_archived=False, is_featured_release=True)\
                .order_by('-major_version','-minor_version','-point_version','-build_version')[0]
            one_app['platform'] = 'ios'
            one_app['releaseDate'] = release.timestamp
            one_app['releaseVersion'] = '{0}.{1}.{2}.{3}'.format(release.major_version,release.minor_version,release.point_version,release.build_version)
            one_app['id'] = release.id
            one_app['description'] = release.ios_project.project_overview.description
            one_app['icon'] = release.ios_project.project_overview.icon
            apps_to_display.append(copy.copy(one_app))
        except IndexError or AndroidRelease.DoesNotExist:
            pass
    sort = sorted(apps_to_display, key=itemgetter('releaseDate'), reverse=True)
    apps_to_display = sort
    return render(request, 'applab/home.html', {'apps': apps_to_display})

def login(request):
    return render(request, 'applab/templates/registration/login.html')

@login_required()
def app_release(request,platform,release_id):
    user_agent = get_user_agent(request)
    request.session['platform'] = platform.lower()
    # if request.META['HTTP_USER_AGENT'].find('iPhone') != -1:
    #     groupSize = 1
    # elif request.META['HTTP_USER_AGENT'].find('iPad') != 1:
    #     groupSize = 2
    # else:
    groupSize = 4
    historyLimit = 6

    # appTitle = ' '.join(project_title.split('-')[1:-4])
    # appRelease = project_title.rsplit('-')[-4:]
    if platform == 'ios':
        curRelease = IosRelease.objects.select_related('ios_project__project_overview__project').filter(id=release_id, is_archived=False)[0]
        overview = curRelease.ios_project.project_overview

        # previous releases should consider all releases for overall Project
        previousReleases = IosRelease.objects.select_related('ios_project__project_overview__project')\
            .filter(is_archived=False, ios_project__project_overview__project_id = curRelease.ios_project.project_overview.project.id)\
            .exclude(id=curRelease.id).order_by('-major_version','-minor_version','-point_version','-build_version')[:historyLimit+1]

        # get latest, non-archived, release, NOT filtered by featured release
        latestRelease = IosRelease.objects.filter(ios_project__project_overview__project_id = overview.project.id, is_archived=False)\
            .order_by('-major_version','-minor_version','-point_version','-build_version')[0]

    elif platform == 'android':
        curRelease = AndroidRelease.objects.select_related('android_project__project_overview__project').filter(id=release_id, is_archived=False)[0]
        overview = curRelease.android_project.project_overview

        # previous releases should consider all releases for overall Project
        previousReleases = AndroidRelease.objects.select_related('android_project__project_overview__project')\
            .filter(is_archived=False, android_project__project_overview__project_id = curRelease.android_project.project_overview.project.id)\
            .exclude(id=curRelease.id).order_by('-major_version','-minor_version','-point_version','-build_version')[:historyLimit+1]

        # get latest, non-archived, release, NOT filtered by featured release
        latestRelease = AndroidRelease.objects.filter(android_project__project_overview__project_id = overview.project.id, is_archived=False)\
            .order_by('-major_version','-minor_version','-point_version','-build_version')[0]

    #screenshots = ProjectOverviewScreenshot.objects.filter(project_overview = overview.project_id)
    screenshots = ProjectOverviewScreenshot.objects.filter(project_overview = overview.id)
    appDetail = {
        'overview' : overview,
        'currentRelease' : curRelease,
        'previousReleases' : previousReleases,
        'latestRelease' : latestRelease,
        'screenshotGroups4': [screenshots[i:i + groupSize] for i in range(0, len(screenshots), groupSize)],
        'screenshotGroups3': [screenshots[i:i + 3] for i in range(0, len(screenshots), 3)],
        'screenshotGroups2': [screenshots[i:i + 2] for i in range(0, len(screenshots), 2)],
        'screenshotGroups1':[screenshots[i:i + 1] for i in range(0, len(screenshots), 1)],
        'title': overview.project.title,
        'platform': platform,
        'releaseVersion': '{0}.{1}.{2}.{3}'.format(curRelease.major_version,curRelease.minor_version,curRelease.point_version,curRelease.build_version),
        'latestVersion' : '{0}.{1}.{2}.{3}'.format(latestRelease.major_version,latestRelease.minor_version,latestRelease.point_version,latestRelease.build_version),
    }
    if str.lower(platform) == 'android':
        appDetail['app_identifier'] = curRelease.android_project.application_id
    elif str.lower(platform) == 'ios':
        appDetail ['app_identifier'] = curRelease.ios_project.bundle_id
    #appDetail.appRelease = '{0}.{1}.{2}.{3}'.format(appDetail.major_version,appDetail.minor_version,appDetail.point_version,appDetail.build_version)
    return render(request,'applab/app-release-page.html/',{
        'appDetail' : appDetail,
    })

# platform_page should display only the latest, non-archived release for the respective platform for each non-archived project.

@login_required()
def platform_page(request,platform,sortfield=None):
    request.session['platform'] = platform.lower()

    platform_app = {'platform' : platform, 'apps': []}

    # Get all non-archived project objects.
    avail_apps = Project.objects.filter(is_archived=False)

    # Iterate through each project to set the apps which will be passed to the template.
    for app in avail_apps:
        one_app = {}
        one_app['title'] = app.title
        if str.lower(platform) == 'android':
            try:
                # Select latest release, not filtered_by_featured for current project and append to dictionary to pass to template.
                release = AndroidRelease.objects.filter(android_project__project_overview__project_id = app.id, is_archived=False)\
                    .order_by('-major_version','-minor_version','-point_version','-build_version')[0]
                one_app['platform'] = 'android'
                one_app['releaseDate'] = release.timestamp
                one_app['releaseVersion'] = '{0}.{1}.{2}.{3}'.format(release.major_version,release.minor_version,release.point_version,release.build_version)
                one_app['id'] = release.id
                one_app['description'] = release.android_project.project_overview.description
                one_app['icon'] = release.android_project.project_overview.icon
                platform_app['apps'].append(copy.copy(one_app))
            except IndexError:
                pass
        elif str.lower(platform) == 'ios':
            try:
                # Select latest release, not filtered_by_featured for current project and append to dictionary to pass to template.
                release = IosRelease.objects.filter(ios_project__project_overview__project_id = app.id, is_archived=False)\
                    .order_by('-major_version','-minor_version','-point_version','-build_version')[0]
                one_app['platform'] = 'ios'
                one_app['releaseDate'] = release.timestamp
                one_app['releaseVersion'] = '{0}.{1}.{2}.{3}'.format(release.major_version,release.minor_version,release.point_version,release.build_version)
                one_app['id'] = release.id
                one_app['description'] = release.ios_project.project_overview.description
                one_app['icon'] = release.ios_project.project_overview.icon
                platform_app['apps'].append(copy.copy(one_app))
            except IndexError:
                pass

    if sortfield:
        sortfield = sortfield.lower()
        if sortfield =='sortname':
            sort = sorted(platform_app['apps'], key=itemgetter('title'))
            platform_app['apps'] = sort
        if sortfield =='sortnamedesc':
            sortfield = '-'+ platform + '_project__project_overview__project__title'
        elif sortfield == 'sortreleasedate':
            sort = sorted(platform_app['apps'], key=itemgetter('releaseDate'), reverse=True)
            platform_app['apps'] = sort
    else:
        sort = sorted(platform_app['apps'], key=itemgetter('releaseDate'), reverse=True)
        platform_app['apps'] = sort

    return render(request,'applab/platform-page.html/', {
        'platform_app' : platform_app
    })

@login_required()
def app_download(request, platform, release_id):
    user_agent = get_user_agent(request)
    if str.lower(platform) == "ios":
        app = IosRelease.objects.select_related('ios_project__project_overview__project').filter(id=release_id)[0]
        ipa_file_url = request.build_absolute_uri(app.ipa_file.url)
        if user_agent.os.family == "iOS":
            response = write_manifest_send(request, app, ipa_file_url)
            return response
        else:
            file_name = app.ios_project.project_overview.project.project_code_name
            ipa_file = app.ipa_file
            response = HttpResponse(FileWrapper(ipa_file), content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename=%s.ipa' % file_name

            return response

    elif str.lower(platform) == "android":
        app = AndroidRelease.objects.select_related('android_project__project_overview__project').filter(id=release_id)[0]

        apk= app.apk_file
        file_name = app.android_project.project_overview.project.project_code_name
        response = HttpResponse(apk, content_type='application/vnd.android.package-archive')
        response['Content-Disposition'] = 'attachment; filename=%s.apk' % file_name

        return response
