from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime # To Parse input DateTime into Python Date Time Object
import logging

logger = logging.getLogger(__name__)

from dokter_management_app.models import CustomUser, SessionYearModel, Courses, Subjects, Dokters, Attendance, AttendanceReport, LeaveReportDokter, FeedBackDokter


def dokter_home(request):
    dokter_obj = Dokters.objects.get(admin=request.user.id)
    total_attendance = AttendanceReport.objects.filter(dokter_id=dokter_obj).count()
    attendance_present = AttendanceReport.objects.filter(dokter_id=dokter_obj, status=True).count()
    attendance_absent = AttendanceReport.objects.filter(dokter_id=dokter_obj, status=False).count()

    course_obj = Courses.objects.get(id=dokter_obj.course_id.id)
    total_subjects = Subjects.objects.filter(course_id=course_obj).count()

    subject_name = []
    data_present = []
    data_absent = []
    subject_data = Subjects.objects.filter(course_id=dokter_obj.course_id)
    for subject in subject_data:
        attendance = Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=True, dokter_id=dokter_obj.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=False, dokter_id=dokter_obj.id).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)
    
    context={
        "total_attendance": total_attendance,
        "attendance_present": attendance_present,
        "attendance_absent": attendance_absent,
        "total_subjects": total_subjects,
        "subject_name": subject_name,
        "data_present": data_present,
        "data_absent": data_absent
    }
    return render(request, "dokter_template/dokter_home_template.html", context)


def dokter_view_attendance(request):
    dokter = Dokters.objects.get(admin=request.user.id) # Getting Logged in Dokter Data
    course = dokter.course_id # Getting Course Enrolled of LoggedIn Dokter
    # course = Courses.objects.get(id=dokter.course_id.id) # Getting Course Enrolled of LoggedIn Dokter
    subjects = Subjects.objects.filter(course_id=course) # Getting the Subjects of Course Enrolled
    context = {
        "subjects": subjects
    }
    return render(request, "dokter_template/dokter_view_attendance.html", context)


def dokter_view_attendance_post(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('dokter_view_attendance')
    else:
        # Getting all the Input Data
        subject_id = request.POST.get('subject')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Parsing the date data into Python object
        start_date_parse = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_parse = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Getting all the Subject Data based on Selected Subject
        subject_obj = Subjects.objects.get(id=subject_id)
        # Getting Logged In User Data
        user_obj = CustomUser.objects.get(id=request.user.id)
        # Getting Dokter Data Based on Logged in Data
        stud_obj = Dokters.objects.get(admin=user_obj)

        # Now Accessing Attendance Data based on the Range of Date Selected and Subject Selected
        attendance = Attendance.objects.filter(attendance_date__range=(start_date_parse, end_date_parse), subject_id=subject_obj)
        # Getting Attendance Report based on the attendance details obtained above
        attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendance, dokter_id=stud_obj)

        # for attendance_report in attendance_reports:
        #     print("Date: "+ str(attendance_report.attendance_id.attendance_date), "Status: "+ str(attendance_report.status))

        # messages.success(request, "Attendacne View Success")

        context = {
            "subject_obj": subject_obj,
            "attendance_reports": attendance_reports
        }

        return render(request, 'dokter_template/dokter_attendance_data.html', context)
# WE don't need csrf_token when using Ajax
@csrf_exempt
def get_dokters(request):
    # Getting Values from Ajax POST 'Fetch Dokter'
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year")

    # Dokters enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    subject_model = Subjects.objects.get(id=subject_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    dokters = Dokters.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)

    # Only Passing Dokter Id and Dokter Name Only
    list_data = []

    for dokter in dokters:
        data_small={"id":dokter.admin.id, "name":dokter.admin.first_name+" "+dokter.admin.last_name}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)

@csrf_exempt
def save_attendance_data(request):
    try:
        # Get Values from Dokter Take Attendance form via AJAX (JavaScript)
        dokter_ids = request.POST.get("dokter_ids")
        subject_id = request.POST.get("subject_id")
        attendance_date = request.POST.get("attendance_date")
        session_year_id = request.POST.get("session_year_id")
        hours_worked_data = request.POST.get("hours_worked")

        subject_model = Subjects.objects.get(id=subject_id)
        session_year_model = SessionYearModel.objects.get(id=session_year_id)

        json_dokter = json.loads(dokter_ids)

        # First Attendance Data is Saved on Attendance Model
        attendance = Attendance(subject_id=subject_model, attendance_date=attendance_date, session_year_id=session_year_model)
        attendance.save()

        for stud in json_dokter:
            dokter = Dokters.objects.get(admin=stud['id'])
            hours_worked = stud['hours_worked']  # Get hours worked for each user
            attendance_report = AttendanceReport(dokter_id=dokter, attendance_id=attendance, status=stud['status'], hours_worked=hours_worked)
            attendance_report.save()

        return HttpResponse("OK")
    except Exception as e:
        logger.error(f"Error saving attendance data: {str(e)}", exc_info=True)
        return HttpResponse(f"Error: {str(e)}")


@csrf_exempt
def get_attendance_dates(request):

    # Getting Values from Ajax POST 'Fetch Dokter'
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year_id")

    # Dokters enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    subject_model = Subjects.objects.get(id=subject_id)
    session_model = SessionYearModel.objects.get(id=session_year)

    # dokters = Dokters.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)
    attendance = Attendance.objects.filter(subject_id=subject_model, session_year_id=session_model)

    # Only Passing Dokter Id and Dokter Name Only
    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "session_year_id":attendance_single.session_year_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def get_attendance_dokter(request):
    # Getting Values from Ajax POST 'Fetch Dokter'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Dokter Id and Dokter Name Only
    list_data = []

    for dokter in attendance_data:
        data_small={"id":dokter.dokter_id.admin.id, "name":dokter.dokter_id.admin.first_name+" "+dokter.dokter_id.admin.last_name, "status":dokter.status, "jumlah jam":dokter.hours_worked}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Attendance, Dokters, AttendanceReport

@csrf_exempt
def update_attendance_data(request):
    try:
        dokter_data = json.loads(request.POST.get("dokter_data"))
        attendance_date = request.POST.get("attendance_date")

        if not dokter_data or not attendance_date:
            return JsonResponse({"status": "error", "message": "Missing required parameters."})

        attendance = Attendance.objects.get(id=attendance_date)

        for stud in dokter_data:
            dokter = Dokters.objects.get(admin=stud['id'])
            try:
                attendance_report = AttendanceReport.objects.get(dokter_id=dokter, attendance_id=attendance)
            except AttendanceReport.DoesNotExist:
                attendance_report = AttendanceReport(dokter_id=dokter, attendance_id=attendance)
            attendance_report.status = stud['status']
            attendance_report.hours_worked = stud['hours_worked'] if stud['status'] == 1 else 0
            attendance_report.save()

        return JsonResponse({"status": "OK"})
    except Attendance.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Attendance record not found."})
    except Dokters.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Dokter record not found."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


def dokter_apply_leave(request):
    dokter_obj = Dokters.objects.get(admin=request.user.id)
    leave_data = LeaveReportDokter.objects.filter(dokter_id=dokter_obj)
    context = {
        "leave_data": leave_data
    }
    return render(request, 'dokter_template/dokter_apply_leave.html', context)


def dokter_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('dokter_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        dokter_obj = Dokters.objects.get(admin=request.user.id)
        try:
            leave_report = LeaveReportDokter(dokter_id=dokter_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
            leave_report.save()
            messages.success(request, "Applied for Leave.")
            return redirect('dokter_apply_leave')
        except:
            messages.error(request, "Failed to Apply Leave")
            return redirect('dokter_apply_leave')


def dokter_feedback(request):
    dokter_obj = Dokters.objects.get(admin=request.user.id)
    feedback_data = FeedBackDokter.objects.filter(dokter_id=dokter_obj)
    context = {
        "feedback_data": feedback_data
    }
    return render(request, 'dokter_template/dokter_feedback.html', context)


def dokter_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('dokter_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        dokter_obj = Dokters.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackDokter(dokter_id=dokter_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('dokter_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('dokter_feedback')


def dokter_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    dokter = Dokters.objects.get(admin=user)
    context={
        "user": user,
        "dokter": dokter
    }
    return render(request, 'dokter_template/dokter_profile.html', context)


def dokter_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('dokter_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()

            dokter = Dokters.objects.get(admin=customuser.id)
            dokter.address = address
            dokter.save()
            
            messages.success(request, "Profile Updated Successfully")
            return redirect('dokter_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('dokter_profile')

def dokter_take_attendance(request):
    dokter = Dokters.objects.get(admin=request.user.id) 
    course = dokter.course_id
    subjects = Subjects.objects.filter(course_id=course)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years,
    }
    return render(request, "dokter_template/dokter_attendance_template.html", context)

def dokter_update_attendance(request):
    dokter = Dokters.objects.get(admin=request.user.id) 
    course = dokter.course_id
    subjects = Subjects.objects.filter(course_id=course)
    session_years = SessionYearModel.objects.all()
    
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "dokter_template/update_attendance_template.html", context)





