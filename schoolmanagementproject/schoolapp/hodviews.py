from django.shortcuts import render,redirect
from schoolapp.models import *
from django.contrib import messages
from django.views.generic import ListView
from schoolapp.forms import *
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import json

def HomeView(request):
    student_count1=Students.objects.all().count()
    staff_count=Staffs.objects.all().count()
    subject_count=Subjects.objects.all().count()
    course_count=Courses.objects.all().count()

    course_all=Courses.objects.all()
    course_name_list=[]
    subject_count_list=[]
    student_count_list_in_course=[]
    for course in course_all:
        subjects=Subjects.objects.filter(course_id=course.id).count()
        students=Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)

    subjects_all=Subjects.objects.all()
    subject_list=[]
    student_count_list_in_subject=[]
    for subject in subjects_all:
        course=Courses.objects.get(id=subject.course_id.id)
        student_count=Students.objects.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)

    staffs=Staffs.objects.all()
    attendance_present_list_staff=[]
    attendance_absent_list_staff=[]
    staff_name_list=[]
    for staff in staffs:
        subject_ids=Subjects.objects.filter(staff_id=staff.admin.id)
        attendance=Attendance.objects.filter(subject_id__in=subject_ids).count()
        leaves=LeaveReportStaff.objects.filter(staff_id=staff.id,leave_status=1).count()
        attendance_present_list_staff.append(attendance)
        attendance_absent_list_staff.append(leaves)
        staff_name_list.append(staff.admin.username)

    students_all=Students.objects.all()
    attendance_present_list_student=[]
    attendance_absent_list_student=[]
    student_name_list=[]
    for student in students_all:
        attendance=AttendanceReport.objects.filter(student_id=student.id,status=True).count()
        absent=AttendanceReport.objects.filter(student_id=student.id,status=False).count()
        leaves=LeaveReportStudent.objects.filter(student_id=student.id,leave_status=1).count()
        attendance_present_list_student.append(attendance)
        attendance_absent_list_student.append(leaves+absent)
        student_name_list.append(student.admin.username)


    return render(request,"hod_template/Hod_home.html",{"student_count":student_count1,"staff_count":staff_count,"subject_count":subject_count,"course_count":course_count,"course_name_list":course_name_list,"subject_count_list":subject_count_list,"student_count_list_in_course":student_count_list_in_course,"student_count_list_in_subject":student_count_list_in_subject,"subject_list":subject_list,"staff_name_list":staff_name_list,"attendance_present_list_staff":attendance_present_list_staff,"attendance_absent_list_staff":attendance_absent_list_staff,"student_name_list":student_name_list,"attendance_present_list_student":attendance_present_list_student,"attendance_absent_list_student":attendance_absent_list_student})

def admin_profile(request):
    if request.method=='POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        try:
            user=CustomUser.objects.get(id=request.user.id)
            user.first_name=first_name
            user.last_name=last_name
            user.save()
            messages.success(request,"Successfully Saved the details")
            return redirect('admin_profile')
        except:
            messages.error(request,"Unable to save data")
            return redirect('admin_profile')
    else:
        user=CustomUser.objects.get(id=request.user.id)
    return render(request,"hod_template/admin_profile.html",{'user':user})



def add_staff_view(request):
    if request.method=='POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        password=request.POST.get('password')
        address=request.POST.get('address')
        username=request.POST.get('username')
        try:
            user=CustomUser.objects.create_user(username=username,first_name=first_name,last_name=last_name,email=email,password=password,user_type=2)
            user.staffs.address=address
            user.save()
            messages.success(request,'Staff info added successfully!!')
            return redirect('add_staff')
        except:
            messages.error(request,'Failed to add staff!!')
            return redirect('add_staff')
    else:
        return render(request,'hod_template/add_staff.html')



def add_student_view(request):
    if request.method=="POST":
        form=AddStudentForm(request.POST,request.FILES)
        if form.is_valid():
            first_name=form.cleaned_data["first_name"]
            last_name=form.cleaned_data["last_name"]
            username=form.cleaned_data["username"]
            email=form.cleaned_data["email"]
            password=form.cleaned_data["password"]
            address=form.cleaned_data["address"]
            session_year_id=form.cleaned_data["session_year_id"]
            course_id=form.cleaned_data["course"]
            gender=form.cleaned_data["gender"]

            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)
            try:
                user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=3)
                user.students.address=address
                course_obj=Courses.objects.get(id=course_id)
                user.students.course_id=course_obj
                session_year=SessionYearModel.object.get(id=session_year_id)
                user.students.session_year_id=session_year
                user.students.gender=gender
                user.students.profile_pic=profile_pic_url
                user.save()
                messages.success(request,"Successfully Added Student")
                return redirect("add_student")
            except:
                messages.error(request,"Failed to Add Student")
                return redirect("add_student")
        else:
            form=AddStudentForm(request.POST)
            return render(request, "hod_template/add_student.html", {"form": form})
    form=AddStudentForm()
    return render(request,"hod_template/add_student.html",{"form":form})

def edit_student_view(request,student_id):
    if request.method=='POST':
        print('post')
        student_id=request.session.get("student_id")
        if student_id==None:
            print('student is is none')
            return redirect("manage_student")
        form=EditStudentForm(request.POST,request.FILES)
        if form.is_valid():
            first_name=form.cleaned_data["first_name"]
            last_name=form.cleaned_data["last_name"]
            username=form.cleaned_data["username"]
            email=form.cleaned_data["email"]
            address=form.cleaned_data["address"]
            session_year_id=form.cleaned_data["session_year_id"]
            course_id=form.cleaned_data["course"]
            gender=form.cleaned_data["gender"]
            if request.FILES.get("profile_pic",False):
                print('profile pic')
                profile_pic=request.FILES['profile_pic']
                fs=FileSystemStorage()
                filename=fs.save(profile_pic.name,profile_pic)
                profile_pic_url=fs.url(filename)
            else:
                profile_pic=None
            try:
                user=CustomUser.objects.get(id=student_id)
                user.first_name=first_name
                user.last_name=last_name
                user.username=username
                user.email=email
                user.save()
                student=Students.objects.get(admin=student_id)
                student.address=address
                student.gender=gender
                course=Courses.objects.get(id=course_id)
                student.course_id=course
                session=SessionYearModel.object.get(id=session_year_id)
                student.session_year_id=session
                if profile_pic_url!=None:
                    print('profile')
                    student.profile_pic=profile_pic_url
                student.save()
                del request.session['student_id']
                messages.success(request,'Student Data Updated Successfully')
                return redirect('manage_student')
            except:
                print('except')
                messages.error(request,"Unable to edit student")
                return redirect("manage_student" )
        else:
            form=EditStudentForm(request.POST)
            student=Students.objects.get(admin=student_id)
            return redirect('manage_student')
    else:
        request.session['student_id']=student_id
        student=Students.objects.get(admin=student_id)
        form=EditStudentForm()
        form.fields['email'].initial=student.admin.email
        form.fields['first_name'].initial=student.admin.first_name
        form.fields['last_name'].initial=student.admin.last_name
        form.fields['username'].initial=student.admin.username
        form.fields['address'].initial=student.address
        form.fields['course'].initial=student.course_id.id
        form.fields['gender'].initial=student.gender
        form.fields['session_year_id'].initial=student.session_year_id.id
    return render(request,"hod_template/edit_student.html",{"form":form,"id":student_id,"username":student.admin.username})

def manage_student_view(request):
    students=Students.objects.all()
    return render(request,'hod_template/manage_student.html',{'students':students})


def manage_staff_view(request):
    staff_info=Staffs.objects.all()
    return render(request,'hod_template/manage_staff.html',{'staff_info':staff_info})

def edit_staff_view(request,staff_id):
    if request.method=='POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        address=request.POST.get('address')
        username=request.POST.get('username')

        try:
            user=CustomUser.objects.get(id=staff_id)
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            user.username=username
            user.save()

            staff_model=Staffs.objects.get(admin=staff_id)
            staff_model.address=address
            staff_model.save()
            messages.success(request,'Staff details updated successfully!!')
            return redirect('edit_staff', staff_id=staff_id)
        except:
            messages.error(request,'Failed to update staff details!!')
            return redirect('edit_staff', staff_id=staff_id)
    else:
        staff=Staffs.objects.get(admin=staff_id)
    return render(request,'hod_template/edit_staff.html',{'staff':staff,'staff_id':staff_id})





def add_course_view(request):
    if request.method=='POST':
        course=request.POST.get('course_name')
        course_name=course.upper()
        try:
            course=Courses.objects.filter(course_name=course_name).count()
            if course !=0:
                messages.error(request,'Course Name Already exists!!')
                return redirect('add_course')
            course_name=Courses.objects.create(course_name=course_name)
            course_name.save()
            messages.success(request,'Course Name Added Successfully!!')
            return redirect('add_course')
        except:
            messages.error(request,'Unable to add Course!!')
            return redirect('add_course')
    return render(request,'hod_template/add_course.html')

def manage_course_view(request):
    courses=Courses.objects.all()
    return render(request,'hod_template/manage_course.html',{'courses':courses})

def edit_course_view(request,course_id):
    if request.method=='POST':
        course=request.POST.get('course_name')
        course_name=course.upper()
        course=Courses.objects.get(id=course_id)
        course.course_name=course_name
        course.save()
        return redirect('manage_course')
    courses=Courses.objects.get(id=course_id)
    return render(request,'hod_template/edit_course.html',{'courses':courses})

def add_subject_view(request):
    if request.method=='POST':
        subject=request.POST.get('subject')
        course_id=request.POST.get('course')
        course=Courses.objects.get(id=course_id)
        staff_id=request.POST.get('staff')
        staff=CustomUser.objects.get(id=staff_id)
        try:
            subject=Subjects.objects.create(subject_name=subject,course_id=course,staff_id=staff)
            subject.save()
            messages.success(request,'Subject details added successfully!!')
            return redirect('add_subject')
        except:
            messages.error(request,'Unable to add the subject details!!')
            return redirect('add_subject')
    courses=Courses.objects.all()
    staffs=CustomUser.objects.filter(user_type=2)
    return render(request,'hod_template/add_subject.html',{'courses':courses,'staffs':staffs})

def manage_subject_view(request):
    subjects=Subjects.objects.all()
    return render(request,'hod_template/manage_subject.html',{'subjects':subjects})

def edit_subject_view(request,subject_id):
    if request.method=='POST':
        subject_id=request.POST.get('subject_id')
        subject_name=request.POST.get('subject_name')
        course_id=request.POST.get('course')
        staff_id=request.POST.get('staff')
        try:
            subject=Subjects.objects.get(id=subject_id)
            subject.subject_name=subject_name
            staff=CustomUser.objects.get(id=staff_id)
            subject.staff_id=staff
            course=Courses.objects.get(id=course_id)
            subject.course_id=course
            subject.save()
            messages.success(request,'Subject details updated successfully!!')
            return redirect('manage_subject')
        except:
            messages.error(request,'Unable to edit subject details!!')
            return redirect('manage_subject')
    else:
        subject=Subjects.objects.get(id=subject_id)
        courses=Courses.objects.all()
        staffs=CustomUser.objects.filter(user_type=2)
    return render(request,'hod_template/edit_subject.html',{'subject':subject,'staffs':staffs,'courses':courses,"id":subject_id})

def manage_session_view(request):
    if request.method=='POST':
        start_year=request.POST.get('start_year')
        end_year=request.POST.get('end_year')
        try:
            year=SessionYearModel(session_start_year=start_year,session_end_year=end_year)
            year.save()
            messages.success(request,'Year Added Successfully!!')
            return redirect('manage_session')
        except:
            messages.error(request,'Unable to add the selected year!!')
            return redirect('manage_session')
    return render(request,'hod_template/manage_session.html')

def student_feedback_view(request):
    if request.method=='POST':
        id=request.POST.get("id")
        feedback_reply=request.POST.get('feedback_reply')
        try:
            reply=FeedBackStudent.objects.get(id=id)
            reply.feedback_reply=feedback_reply
            reply.save()
            messages.success(request,"Reply Sent Successfully!!")
            return redirect('admin_student_feedback')
        except:
            messages.error(request,"unable to send reply!!")
            return redirect('admin_student_feedback')
    else:
        students=FeedBackStudent.objects.all()
    return render(request,"hod_template/student_feedback.html",{'students':students})


def staff_feedback_view(request):
    if request.method=='POST':
        id=request.POST.get("id")
        feedback_reply=request.POST.get('feedback_reply')
        try:
            reply=FeedBackStaffs.objects.get(id=id)
            reply.feedback_reply=feedback_reply
            reply.save()
            messages.success(request,"Reply Sent Successfully!!")
            return redirect('admin_staff_feedback')
        except:
            messages.error(request,"unable to send reply!!")
            return redirect('admin_staff_feedback')
    else:
        staffs=FeedBackStaffs.objects.all()
    return render(request,"hod_template/staff_feedback.html",{'staffs':staffs})

def student_leave_view(request):
    students=LeaveReportStudent.objects.all()
    return render(request,"hod_template/student_leave.html",{'students':students})

def approve_student_leave_view(request,leave_id):
    leave=LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return redirect("admin_student_leave")

def disapprove_student_leave_view(request,leave_id):
    leave=LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return redirect("admin_student_leave")

def staff_leave_view(request):
    staffs=LeaveReportStaff.objects.all()
    return render(request,"hod_template/staff_leave.html",{'staffs':staffs})

def approve_staff_leave_view(request,leave_id):
    leave=LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return redirect("admin_staff_leave")

def disapprove_staff_leave_view(request,leave_id):
    leave=LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return redirect("admin_staff_leave")

def staff_notification_view(request):
    if request.method=='POST':
        staff_id=request.POST.get('staff_id')
        message=request.POST.get('message')
        staff=Staffs.objects.get(admin=staff_id)
        try:
            notify=NotificationStaffs(staff_id=staff)
            notify.message=message
            notify.save()
            messages.success(request,"Notification sent successfully!!")
            return redirect('admin_staff_notification')
        except:
            messages.error(request,"Unable to send Notification!!")
            return redirect('admin_staff_notification')
    else:
        staffs=Staffs.objects.all()
    return render(request,"hod_template/staff_notification.html",{'staffs':staffs})
def student_notification_view(request):
    if request.method=='POST':
        student_id=request.POST.get('student_id')
        message=request.POST.get('message')
        student=Students.objects.get(admin=student_id)
        try:
            notify=NotificationStudent(student_id=student)
            notify.message=message
            notify.save()
            messages.success(request,"Notification sent successfully!!")
            return redirect('admin_student_notification')
        except:
            messages.error(request,"Unable to send Notification!!")
            return redirect('admin_student_notification')
    else:
        students=Students.objects.all()
    return render(request,"hod_template/student_notification.html",{'students':students})

def view_attendance_view(request):
    subjects=Subjects.objects.all()
    sessions=SessionYearModel.object.all()
    return render(request,"hod_template/view_attendance.html",{'subjects':subjects,'sessions':sessions})

@csrf_exempt
def admin_get_attendance_dates(request):
    subject=request.POST.get("subject")
    session_year_id=request.POST.get("session_year_id")
    print(subject)
    print(session_year_id)
    subject_obj=Subjects.objects.get(id=subject)
    session_year_obj=SessionYearModel.object.get(id=session_year_id)
    attendances=Attendance.objects.filter(subject_id=subject_obj,session_year_id=session_year_obj)
    attendance_obj=[]
    for attendance in attendances:
        data={"id":attendance.id,"attendance_date":str(attendance.attendance_date)}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj),safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)
    list_data=[]

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id,"name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name,"status":student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)
