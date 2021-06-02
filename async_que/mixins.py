from django.conf import settings


class EnumBase(object):

    @classmethod
    def display(cls, value):
        if value:
            index = [x[0] for x in cls.choices].index(value)
            choice = cls.choices[index]
            display = choice[1]
        else:
            display = 'None'
        return display


class ProtectedAdminMixin(object):

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG:
            return True
        else:
            return False