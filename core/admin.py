from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User

from core.admin_site import cafe_admin_site

cafe_admin_site.register(User, UserAdmin)
cafe_admin_site.register(Group, GroupAdmin)
