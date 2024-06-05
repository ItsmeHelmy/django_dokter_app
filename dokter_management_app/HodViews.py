from datetime import date
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.db.models import Sum, Q
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json

from dokter_management_app.models import CustomUser, Courses, Subjects, Dokters, SessionYearModel, FeedBackDokter, LeaveReportDokter, Attendance, AttendanceReport
from .forms import AddDokterForm, EditDokterForm

def admin_home(request):
    all_dokter_count = Dokters.objects.all().count()
    subject_count = Subjects.objects.all().count()
    course_count = Courses.objects.all().count()

    # Total Subjects and dokters in Each Course
    course_all = Courses.objects.all()
    course_name_list = []
    subject_count_list = []
    dokter_count_list_in_course = []

    for course in course_all:
        subjects = Subjects.objects.filter(course_id=course.id).count()
        dokters = Dokters.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        dokter_count_list_in_course.append(dokters)
    
    subject_all = Subjects.objects.all()
    subject_list = []
    dokter_count_list_in_subject = []
    for subject in subject_all:
        course = Courses.objects.get(id=subject.course_id.id)
        dokter_count = Dokters.objects.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name)
        dokter_count_list_in_subject.append(dokter_count)

    # For Dokters
    dokter_attendance_present_list=[]
    dokter_attendance_leave_list=[]
    dokter_name_list=[]

    dokters = Dokters.objects.all()
    for dokter in dokters:
        attendance = AttendanceReport.objects.filter(dokter_id=dokter.id, status=True).count()
        absent = AttendanceReport.objects.filter(dokter_id=dokter.id, status=False).count()
        leaves = LeaveReportDokter.objects.filter(dokter_id=dokter.id, leave_status=1).count()
        dokter_attendance_present_list.append(attendance)
        dokter_attendance_leave_list.append(leaves+absent)
        dokter_name_list.append(dokter.admin.first_name)

    context={
        "all_dokter_count": all_dokter_count,
        "subject_count": subject_count,
        "course_count": course_count,
        "course_name_list": course_name_list,
        "subject_count_list": subject_count_list,
        "dokter_count_list_in_course": dokter_count_list_in_course,
        "subject_list": subject_list,
        "dokter_count_list_in_subject": dokter_count_list_in_subject,
        "dokter_attendance_present_list": dokter_attendance_present_list,
        "dokter_attendance_leave_list": dokter_attendance_leave_list,
        "dokter_name_list": dokter_name_list,
    }
    return render(request, "hod_template/home_content.html", context)

def add_course(request):
    return render(request, "hod_template/add_course_template.html")


def add_course_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_course')
    else:
        course = request.POST.get('course')
        try:
            course_model = Courses(course_name=course)
            course_model.save()
            messages.success(request, "Berhasil membuat jadwal jaga!")
            return redirect('add_course')
        except:
            messages.error(request, "Gagal membuat jadwal jaga!")
            return redirect('add_course')


def manage_course(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses
    }
    return render(request, 'hod_template/manage_course_template.html', context)


def edit_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    context = {
        "course": course,
        "id": course_id
    }
    return render(request, 'hod_template/edit_course_template.html', context)


def edit_course_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course')

        try:
            course = Courses.objects.get(id=course_id)
            course.course_name = course_name
            course.save()

            messages.success(request, "Jadwal jaga berhasil diupdate.")
            return redirect('/edit_course/'+course_id)

        except:
            messages.error(request, "Jadwal jaga gagal diupdate.")
            return redirect('/edit_course/'+course_id)


def delete_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    try:
        course.delete()
        messages.success(request, "Jadwal jaga berhasil dihapus.")
        return redirect('manage_course')
    except:
        messages.error(request, "Jadwal jaga gagal dihapus.")
        return redirect('manage_course')


def manage_session(request):
    session_years = SessionYearModel.objects.all()
    context = {
        "session_years": session_years
    }
    return render(request, "hod_template/manage_session_template.html", context)


def add_session(request):
    return render(request, "hod_template/add_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_course')
    else:
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            sessionyear = SessionYearModel(session_start_year=session_start_year, session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Berhasil membuat periode jaga!")
            return redirect("add_session")
        except:
            messages.error(request, "Gagal membuat periode jaga")
            return redirect("add_session")


def edit_session(request, session_id):
    session_year = SessionYearModel.objects.get(id=session_id)
    context = {
        "session_year": session_year
    }
    return render(request, "hod_template/edit_session_template.html", context)


def edit_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('manage_session')
    else:
        session_id = request.POST.get('session_id')
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            session_year = SessionYearModel.objects.get(id=session_id)
            session_year.session_start_year = session_start_year
            session_year.session_end_year = session_end_year
            session_year.save()

            messages.success(request, "Periode jaga berhasil diupdate.")
            return redirect('/edit_session/'+session_id)
        except:
            messages.error(request, "Periode jaga gagal diupdate.")
            return redirect('/edit_session/'+session_id)


def delete_session(request, session_id):
    session = SessionYearModel.objects.get(id=session_id)
    try:
        session.delete()
        messages.success(request, "Periode jaga berhasil dihapus.")
        return redirect('manage_session')
    except:
        messages.error(request, "Periode jaga gagal dihapus.")
        return redirect('manage_session')


def add_dokter(request):
    form = AddDokterForm()
    context = {
        "form": form
    }
    return render(request, 'hod_template/add_dokter_template.html', context)

def add_dokter_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_dokter')
    else:
        form = AddDokterForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            nik = form.cleaned_data['nik']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            mulai_kerja = form.cleaned_data['mulai_kerja']
            session_year_id = form.cleaned_data['session_year_id']
            course_id = form.cleaned_data['course_id']
            besar_honor = form.cleaned_data['besar_honor']
            gender = form.cleaned_data['gender']
            jabatan = form.cleaned_data['jabatan']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)
                
                user.dokters.nik = nik
                user.dokters.address = address

                course_obj = Courses.objects.get(id=course_id)
                user.dokters.course_id = course_obj

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                user.dokters.session_year_id = session_year_obj

                user.dokters.besar_honor = besar_honor
                user.dokters.gender = gender
                user.dokters.mulai_kerja = mulai_kerja
                user.dokters.jabatan = jabatan
                user.dokters.profile_pic = profile_pic_url
                user.save()
                messages.success(request, "Dokter Added Successfully!")
                return redirect('add_dokter')
            except:
                messages.error(request, "Failed to Add Dokter!")
                return redirect('add_dokter')
        else:
            return redirect('add_dokter')


def manage_dokter(request):
    query = request.GET.get('search', '')
    if query:
        dokters = Dokters.objects.filter(
            Q(admin__first_name__icontains=query) |
            Q(admin__last_name__icontains=query) |
            Q(admin__email__icontains=query) |
            Q(jabatan__icontains=query) |
            Q(address__icontains=query)
        )
    else:
        dokters = Dokters.objects.all()

    context = {
        "dokters": dokters,
        "search_query": query,
    }
    return render(request, 'hod_template/manage_dokter_template.html', context)


def edit_dokter(request, dokter_id):
    # Adding Dokter ID into Session Variable
    request.session['dokter_id'] = dokter_id

    dokter = Dokters.objects.get(admin=dokter_id)
    form = EditDokterForm()
    # Filling the form with Data from Database
    form.fields['email'].initial = dokter.admin.email
    form.fields['username'].initial = dokter.admin.username
    form.fields['first_name'].initial = dokter.admin.first_name
    form.fields['last_name'].initial = dokter.admin.last_name
    form.fields['nik'].initial = dokter.nik
    form.fields['address'].initial = dokter.address
    form.fields['besar_honor'].initial = dokter.besar_honor
    form.fields['course_id'].initial = dokter.course_id.id
    form.fields['gender'].initial = dokter.gender
    form.fields['mulai_kerja'].initial = dokter.mulai_kerja
    form.fields['session_year_id'].initial = dokter.session_year_id.id

    context = {
        "id": dokter_id,
        "username": dokter.admin.username,
        "form": form
    }
    return render(request, "hod_template/edit_dokter_template.html", context)


def edit_dokter_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        dokter_id = request.session.get('dokter_id')
        if dokter_id == None:
            return redirect('/manage_dokter')

        form = EditDokterForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            nik = form.cleaned_data['nik']
            address = form.cleaned_data['address']
            course_id = form.cleaned_data['course_id']
            besar_honor = form.cleaned_data['besar_honor']
            gender = form.cleaned_data['gender']
            mulai_kerja = form.cleaned_data['mulai_kerja']
            jabatan = form.cleaned_data['jabatan']
            session_year_id = form.cleaned_data['session_year_id']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                # First Update into Custom User Model
                user = CustomUser.objects.get(id=dokter_id)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                user.save()

                # Then Update Dokter Table
                dokter_model = Dokters.objects.get(admin=dokter_id)
                dokter_model.nik = nik
                dokter_model.address = address

                course = Courses.objects.get(id=course_id)
                dokter_model.course_id = course

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                dokter_model.session_year_id = session_year_obj

                dokter_model.besar_honor = besar_honor
                dokter_model.gender = gender
                dokter_model.mulai_kerja = mulai_kerja
                dokter_model.jabatan = jabatan
                if profile_pic_url != None:
                    dokter_model.profile_pic = profile_pic_url
                dokter_model.save()
                # Delete dokter_id SESSION after the data is updated
                del request.session['dokter_id']

                messages.success(request, "Dokter Updated Successfully!")
                return redirect('/edit_dokter/'+dokter_id)
            except:
                messages.success(request, "Failed to Uupdate Dokter.")
                return redirect('/edit_dokter/'+dokter_id)
        else:
            return redirect('/edit_dokter/'+dokter_id)


def delete_dokter(request, dokter_id):
    dokter = Dokters.objects.get(admin=dokter_id)
    try:
        dokter.delete()
        messages.success(request, "Dokter Deleted Successfully.")
        return redirect('manage_dokter')
    except:
        messages.error(request, "Failed to Delete Dokter.")
        return redirect('manage_dokter')


def add_subject(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses,
    }
    return render(request, 'hod_template/add_subject_template.html', context)

def add_subject_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_subject')
    else:
        subject_name = request.POST.get('subject')
        course_id = request.POST.get('course')
        course = Courses.objects.get(id=course_id)
        try:
            subject = Subjects(subject_name=subject_name, course_id=course)
            subject.save()
            messages.success(request, "Berhasil membuat sesi jaga!")
            return redirect('add_subject')
        except:
            messages.error(request, "Gagal membuat sesi jaga!")
            return redirect('add_subject')


def manage_subject(request):
    subjects = Subjects.objects.all()
    context = {
        "subjects": subjects
    }
    return render(request, 'hod_template/manage_subject_template.html', context)


def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    courses = Courses.objects.all()
    context = {
        "subject": subject,
        "courses": courses,
        "id": subject_id
    }
    return render(request, 'hod_template/edit_subject_template.html', context)


def edit_subject_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject')
        course_id = request.POST.get('course')

        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name

            course = Courses.objects.get(id=course_id)
            subject.course_id = course
            
            subject.save()

            messages.success(request, "Sesi jaga berhasil diupdate.")
            # return redirect('/edit_subject/'+subject_id)
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))

        except:
            messages.error(request, "Sesi jaga gagal diupdate.")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))
            # return redirect('/edit_subject/'+subject_id)



def delete_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Sesi jaga berhasil dihapus.")
        return redirect('manage_subject')
    except:
        messages.error(request, "Sesi jaga gagal dihapus.")
        return redirect('manage_subject')


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)



def dokter_feedback_message(request):
    feedbacks = FeedBackDokter.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/dokter_feedback_template.html', context)


@csrf_exempt
def dokter_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackDokter.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")

def dokter_leave_view(request):
    leaves = LeaveReportDokter.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/dokter_leave_view.html', context)

def dokter_leave_approve(request, leave_id):
    leave = LeaveReportDokter.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('dokter_leave_view')


def dokter_leave_reject(request, leave_id):
    leave = LeaveReportDokter.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('dokter_leave_view')

def admin_view_attendance(request):
    subjects = Subjects.objects.all()
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "hod_template/admin_view_attendance.html", context)


from datetime import date
from django.db.models import Sum

def admin_view_gaji(request):
    dokters = Dokters.objects.all()
    dokter_hours = {}
    dokter_dates = {}

    for dokter in dokters:
        total_hours = AttendanceReport.objects.filter(
            dokter_id=dokter,
            attendance_id__subject_id__course_id=dokter.course_id,
            attendance_id__session_year_id=dokter.session_year_id
        ).aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
        dokter_hours[dokter.id] = total_hours

        # Calculate besar_honor based on hours_worked
        dokter.nominal_bayar = total_hours * dokter.besar_honor  # Assuming besar_honor is a field in your Dokters model

        # Calculate the difference between the current date and mulai_kerja
        date1 = date.today()
        date2 = dokter.mulai_kerja

        # Calculate the difference between the two dates
        delta = date1 - date2
        
        # Calculate the number of years and months
        years = delta.days // 365
        months = (delta.days % 365) // 30

        # Store the calculated values in a dictionary
        dokter_dates[dokter.id] = {
            'years': years,
            'months': months,
            'mulai_kerja': date2
        }

    context = {
        'dokters': dokters,
        'dokter_hours': dokter_hours,
        'dokter_dates': dokter_dates
    }
    return render(request, 'hod_template/view_laporan_gaji.html', context)

@csrf_exempt
def admin_get_attendance_dates(request):
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
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "session_year_id":attendance_single.session_year_id.id, "hours_worked":attendance_single.hours_worked}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def admin_get_attendance_dokter(request):
    # Getting Values from Ajax POST 'Fetch Dokter'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Dokter Id and Dokter Name Only
    list_data = []

    for dokter in attendance_data:
        data_small={"id":dokter.dokter_id.admin.id, "name":dokter.dokter_id.admin.first_name+" "+dokter.dokter_id.admin.last_name, "status":dokter.status, "jumlah jam":dokter.attendance_id.hours_worked}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context={
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')

def dokter_profile(requtest):
    pass



