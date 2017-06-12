from django.db import models
from django.utils.timezone import localtime
from django.utils.html import mark_safe
from applab.settings import MEDIA_ROOT

import os.path


class Project(models.Model):
    """ The ProjectTitle is the top level object for all apps and is a foreign key for all ProjectOverview objects. """
    title = models.CharField(max_length=200)
    project_code_name = models.SlugField(max_length=30)    # the code name used to refer to the project, e.g. lydia
    is_archived = models.BooleanField(default=False)       # archived projects will not be listed with active projects

    def __str__(self):
        return self.title


def overview_icon_upload_path(instance, filename):
    return os.path.join(instance.get_overview_path(), "icons", filename)


class ProjectOverview(models.Model):
    """ A ProjectOverview object belongs to a Project and contains text description, an icon, and has multiple screenshots
    as it is a foreign key to the ProjectScreenshot object. The attributes of this object may evolve over time and are
    separated from the Project object
    """
    NO_PLATFORM = ''
    IOS = 'ios'
    ANDROID = 'and'
    WINDOWS_MOBILE = 'win'
    MULTIPLE_PLATFORM = 'mlp'
    PLATFORM_CHOICES = (
        (NO_PLATFORM, 'No Platform'),
        (IOS, 'iOS'),
        (ANDROID, 'Android'),
        (WINDOWS_MOBILE, 'Windows Mobile'),
        (MULTIPLE_PLATFORM, 'Multi-Platform')
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    platform = models.CharField(max_length=3, choices=PLATFORM_CHOICES, default=NO_PLATFORM)
    major_version = models.PositiveSmallIntegerField()
    minor_version = models.PositiveSmallIntegerField()
    date_published = models.DateTimeField(auto_now=True)
    description = models.TextField()
    icon = models.ImageField(upload_to=overview_icon_upload_path)
    source_code_link = models.URLField(blank=True, max_length=200, default="")

    def get_version_string(self):
        return "{}.{}".format(self.major_version, self.minor_version)

    def get_overview_path(self):
        return os.path.join(self.project.project_code_name, "overviews", self.get_version_string())

    def is_ios(self):
        return self.platform in self.IOS

    def is_android(self):
        return self.platform in self.ANDROID

    def is_windows(self):
        return self.platform in self.WINDOWS_MOBILE

    def is_multi_platform(self):
        return self.platform in self.MULTIPLE_PLATFORM

    def icon_image(self):
        return mark_safe('<img src="%s" style="max-height: 100px; max-width: 100px;" />' % self.icon.url)
    icon_image.allow_tags = True

    def platform_readable_name(self):
        for choice in self.PLATFORM_CHOICES:
            if choice[0] == self.platform:
                return choice[1]
        return ''

    def __str__(self):
        return '%s, %s, %s' % (self.project.title, self.platform_readable_name(), self.get_version_string())


def overview_screenshot_upload_path(instance, filename):
    return os.path.join(instance.project_overview.get_overview_path(), "screenshots", filename)


class ProjectOverviewScreenshot(models.Model):
    """ This object is a screenshot of the app, each ProjectAssets object can have multiple screenshots
    """
    project_overview = models.ForeignKey(ProjectOverview, related_name='screenshots')
    screenshot = models.ImageField(upload_to=overview_screenshot_upload_path)

    def screenshot_image(self):
        return mark_safe('<img src="%s" style="max-height: 100px; max-width: 100px;" />' % self.screenshot.url)
    screenshot_image.allow_tags = True

    def __str__(self):
        return self.screenshot.path


class IosProject(models.Model):
    project_overview = models.ForeignKey(ProjectOverview, on_delete=models.CASCADE)
    bundle_id = models.CharField(max_length=100, default="")
    apple_app_store_link = models.URLField(blank=True, max_length=200, default="")

    def __str__(self):
        return '%s, %s' % (self.bundle_id, self.project_overview)


class AndroidProject(models.Model):
    project_overview = models.ForeignKey(ProjectOverview, on_delete=models.CASCADE)
    application_id = models.CharField(max_length=100, default="")
    google_play_link = models.URLField(blank=True, max_length=200, default="")

    def __str__(self):
        return '%s, %s' % (self.application_id, self.project_overview)


class Release(models.Model):
    """ A Release belongs to a Project and contains a version number and a is_archived flag.
    A Release is a foreign key for ReleaseAssets and ReleaseApp """
    major_version = models.PositiveSmallIntegerField()
    minor_version = models.PositiveSmallIntegerField()
    point_version = models.PositiveSmallIntegerField()
    build_version = models.PositiveSmallIntegerField()
    is_archived = models.BooleanField(default=False)
    what_is_new = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    is_featured_release = models.BooleanField(default=False)

    # def __str__(self):
    #     return '%d.%d.%d.%d' % (self.major_version, self.minor_version, self.point_version, self.build_version)


def ipa_upload_path(instance, filename):
    version_path = '%d.%d.%d.%d' % (instance.major_version, instance.minor_version, instance.point_version, instance.build_version)
    platform_path = 'ios'
    return os.path.join(instance.ios_project.project_overview.project.project_code_name, "releases", platform_path,
                        version_path, filename)


class IosRelease(Release):
    ios_project = models.ForeignKey(IosProject, on_delete=models.CASCADE)
    ipa_file = models.FileField(upload_to=ipa_upload_path)

    def __str__(self):
        return '%s %d.%d.%d.%d' % (self.ios_project.project_overview.project.title, self.major_version,
                                   self.minor_version, self.point_version, self.build_version)


def apk_upload_path(instance, filename):
    version_path = '%d.%d.%d.%d' % (instance.major_version, instance.minor_version, instance.point_version, instance.build_version)
    platform_path = 'android'
    return os.path.join(instance.android_project.project_overview.project.project_code_name, "releases", platform_path,
                        version_path, filename)


class AndroidRelease(Release):
    android_project = models.ForeignKey(AndroidProject, on_delete=models.CASCADE)
    apk_file = models.FileField(upload_to=apk_upload_path)

    def __str__(self):
        return '%s %d.%d.%d.%d' % (self.android_project.project_overview.project.title, self.major_version,
                                   self.minor_version, self.point_version, self.build_version)



