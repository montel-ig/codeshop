from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group


# === patch & reload User/UserAdmin ===
User.group_list = lambda self: u', '.join(map(unicode, self.groups.all()))
User.user_info = lambda self: u'{x.username} <{x.email}>'.format(x=self)

UserAdmin.list_display = (u'user_info', 'group_list', 'is_staff')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# === patch & reload Group/GroupAdmin ===
Group.user_list = lambda self: u', '.join(x.user_info()
                                          for x in self.user_set.all())
GroupAdmin.list_display = (u'name', 'user_list')

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


# === extranet models ===
