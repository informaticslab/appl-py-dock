from django.contrib import admin

# Register your models here.
from .models import Project, ProjectOverview, ProjectOverviewScreenshot
from .models import IosProject, IosRelease, AndroidProject, AndroidRelease


admin.site.register(Project)


class ProjectOverviewScreenshotInline(admin.TabularInline):
    model = ProjectOverviewScreenshot
    readonly_fields = ('screenshot_image',)
    fields = ('screenshot_image', 'screenshot')


class ProjectOverviewAdmin(admin.ModelAdmin):
    readonly_fields = ('date_published', 'icon_image')
    fieldsets = [
        (None,              {'fields': ['project', 'platform', 'date_published', 'description']}),
        ('Version Info',   {'fields': ['major_version', 'minor_version']}),
        ('Source Code Link',   {'fields': ['source_code_link']}),
        ('Icon',   {'fields': ['icon_image', 'icon']}),
    ]
    list_filter = ['date_published', 'platform']
    inlines = [ProjectOverviewScreenshotInline]


class IosReleaseAdmin(admin.ModelAdmin):
    model = IosRelease


class IosReleaseInline(admin.TabularInline):
    model = IosRelease
    fields = ['major_version', 'minor_version','point_version', 'build_version']
    #show_change_link = True


class IosProjectAdmin(admin.ModelAdmin):
    inlines = [IosReleaseInline]


admin.site.register(ProjectOverview, ProjectOverviewAdmin)
admin.site.register(IosProject, IosProjectAdmin)
admin.site.register(IosRelease, IosReleaseAdmin)
admin.site.register(AndroidProject)
admin.site.register(AndroidRelease)


