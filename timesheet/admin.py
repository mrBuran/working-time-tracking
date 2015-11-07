from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.timezone import get_current_timezone
from .models import SpentTime, Category, Task, Project, MonthlyReport, \
    MonthlyInvoice, Company, CompanyInvoiceData, UserInvoiceData, Salary


tz = get_current_timezone()
UserModel = get_user_model()


class SpentTimeAdmin(admin.ModelAdmin):
    list_display = ('day', 'period', 'duration_pretty', 'cost', 'task',
                    'comment')
    list_filter = ('start_time', 'task__project__company', 'task__project')
    fields = ('start_time', 'end_time_pretty', 'comment', 'duration', 'task')
    readonly_fields = ('end_time_pretty', )
    date_hierarchy = 'start_time'

    def duration_pretty(self, obj):
        return '%.1f h' % obj.duration

    def end_time_pretty(self, obj):
        return obj.end_time.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')

    def get_queryset(self, request):
        qs = super(SpentTimeAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(worker=request.user)

    def save_model(self, request, obj, form, change):
        obj.worker = request.user
        obj.save()

    end_time_pretty.short_description = 'End time(auto)'
    duration_pretty.short_description = 'Duration'


class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report')

    def report(self, obj):
        return '<a href="{url}">{url}</a'.format(url=obj.filename.url)

    report.short_description = 'Report'
    report.allow_tags = True


class MonthlyInvoiceAdmin(MonthlyReportAdmin):
    pass


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title_pretty', 'progress', 'priority', 'status')
    list_filter = ('project__company', 'project')

    def title_pretty(self, obj):
        return str(obj)

    title_pretty.short_description = 'Title'


class CompanyInvoiceDataInline(admin.StackedInline):
    model = CompanyInvoiceData
    can_delete = False
    verbose_name_plural = 'additional info'


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('title', )
    inlines = (CompanyInvoiceDataInline, )


class UserInvoiceDataInline(admin.StackedInline):
    model = UserInvoiceData
    can_delete = False
    verbose_name_plural = 'additional info'


class ExtendedUserAdmin(UserAdmin):
    inlines = (UserInvoiceDataInline, )

admin.site.register(SpentTime, SpentTimeAdmin)
admin.site.register(Category)
admin.site.register(Task, TaskAdmin)
admin.site.register(Project)
admin.site.register(MonthlyReport, MonthlyReportAdmin)
admin.site.register(MonthlyInvoice, MonthlyInvoiceAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.unregister(UserModel)
admin.site.register(UserModel, ExtendedUserAdmin)
admin.site.register(Salary)
