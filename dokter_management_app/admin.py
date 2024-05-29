from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AdminHOD, Courses, Subjects, Dokters, Attendance, AttendanceReport, LeaveReportDokter, FeedBackDokter, NotificationDokter

# Register your models here.
class UserModel(UserAdmin):
    pass


admin.site.register(CustomUser, UserModel)

admin.site.register(AdminHOD)
admin.site.register(Courses)
admin.site.register(Subjects)
admin.site.register(Dokters)
admin.site.register(Attendance)
admin.site.register(AttendanceReport)
admin.site.register(LeaveReportDokter)
admin.site.register(FeedBackDokter)
admin.site.register(NotificationDokter)
