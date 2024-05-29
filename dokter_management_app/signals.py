# import logging
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Attendance, AttendanceReport

# logger = logging.getLogger(__name__)

# @receiver(post_save, sender=Attendance)
# def update_attendance_report(sender, instance, created, **kwargs):
#     logger.info("Signal received for Attendance: %s", instance.id)
#     if created:
#         AttendanceReport.objects.update_or_create(
#             attendance_id=instance,
#             defaults={'hours_worked': instance.hours_worked}
#         )
#     else:
#         AttendanceReport.objects.filter(attendance_id=instance).update(hours_worked=instance.hours_worked)