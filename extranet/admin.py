from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group

from models import Organization, Repository


# === patch & reload User/UserAdmin ===
User.groups_string = lambda self: u', '.join(map(unicode, self.groups.all()))
User.user_info = lambda self: u'{x.username} <{x.email}>'.format(x=self)

UserAdmin.list_display = (u'user_info', 'groups_string', 'is_staff')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# === patch & reload Group/GroupAdmin ===
Group.users_string = lambda self: u', '.join(x.user_info()
                                             for x in self.user_set.all())
GroupAdmin.list_display = (u'name', 'users_string')

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


# === extranet models ===
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (u'login', u'repositories_string')


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = (u'name', u'synced_at', u'latest_created_issue',
                    u'latest_updated_issue', u'latest_closed_issue')
    actions = ['sync']

    def sync(self, request, queryset):
        for repo in queryset:
            repo._sync()
    sync.short_description = "Sync local issues with Github"
