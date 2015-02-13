from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group

from models import (Project, Need, Organization, Repository, Issue, Hours,
                    HourTag)


# === patch & reload User/UserAdmin ===

User.groups_string = lambda self: u', '.join(map(unicode, self.groups.all()))
User.user_hours = lambda x: sum(h.amount for h in x.hours_set.all())

UserAdmin.list_display = (u'username', 'email', u'user_hours', u'groups_string',
                          u'is_staff')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# === patch & reload Group/GroupAdmin ===

Group.users_string = \
    lambda self: u', '.join(x.username for x in self.user_set.all())
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
    list_display = (u'login', u'repositories_string', u'total_hours')

    def get_readonly_fields(self, request, obj=None):
        return (u'login',) if obj else tuple()


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = (u'name', u'default_project', u'synced_at',
                    u'latest_created_issue', u'latest_updated_issue',
                    u'latest_closed_issue', u'total_hours')
    actions = ['sync']

    def get_readonly_fields(self, request, obj=None):
        fields = (u'synced_at',)
        return (u'organization', u'name') + fields if obj else fields

    def sync(self, request, queryset):
        for repo in queryset:
            repo._sync()
    sync.short_description = "Sync local issues with Github"


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (u'__unicode__', u'synced_at', u'need', u'created_at',
                    u'closed_at', u'total_hours')
    list_filter = (u'repository',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "need":
            # sort Needs by project and name in admin
            # TODO: filter our closed needs
            kwargs["queryset"] = Need.objects.order_by('project', 'name')
        return super(IssueAdmin, self).formfield_for_foreignkey(db_field,
                                                                request,
                                                                **kwargs)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (u'name', u'customer_team', u'coder_team', u'latest_need',
                    u'repositories_string', u'total_hours')


@admin.register(Need)
class NeedAdmin(admin.ModelAdmin):
    list_display = (u'project', u'name', u'is_estimate_requested',
                    u'estimate_finished_at', u'created_at', u'total_hours')


@admin.register(HourTag)
class HourTagAdmin(admin.ModelAdmin):
    list_display = (u'name', u'total_hours',)


@admin.register(Hours)
class HoursAdmin(admin.ModelAdmin):
    list_display = (u'coder', u'project', u'date', u'amount', u'tags_string',
                    u'issue', u'ticket_info')
    list_filter = (u'coder', u'project')
    readonly_fields = (u'coder',  u'date', u'start_time', u'end_time',
                       u'amount', u'comment', u'input_data_json',
                       u'created_at', u'updated_at',)
