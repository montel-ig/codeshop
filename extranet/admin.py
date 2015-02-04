from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group

from models import Project, Organization, Repository


# === patch & reload User/UserAdmin ===

User.groups_string = lambda self: u', '.join(map(unicode, self.groups.all()))
User.user_info = lambda x: u'<{}>'.format(x.email) if x.email else x.username

UserAdmin.list_display = (u'user_info', u'groups_string', u'is_staff')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# === patch & reload Group/GroupAdmin ===

Group.users_string = \
    lambda self: u', '.join(x.user_info() for x in self.user_set.all())
Group.customer_projects_string = \
    lambda self: u', '.join(map(unicode, self.customer_projects.all()))
Group.code_projects_string = \
    lambda self: u', '.join(map(unicode, self.code_projects.all()))

GroupAdmin.list_display = \
    (u'name', u'users_string', u'customer_projects_string',
     u'code_projects_string')

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


# === extranet models ===

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (u'login', u'repositories_string')

    def get_readonly_fields(self, request, obj=None):
        return (u'login',) if obj else tuple()


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = (u'name', u'synced_at', u'latest_created_issue',
                    u'latest_updated_issue', u'latest_closed_issue')
    actions = ['sync']

    def get_readonly_fields(self, request, obj=None):
        fields = (u'synced_at',)
        return (u'organization', u'name') + fields if obj else fields

    def sync(self, request, queryset):
        for repo in queryset:
            repo._sync()
    sync.short_description = "Sync local issues with Github"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (u'name', u'customer_team', u'coder_team')
