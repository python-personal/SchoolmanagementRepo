from django.shortcuts import render,redirect
from schoolapp.models import *
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
from django.core import serializers
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
import datetime

def student_home_view(request):
    student_obj=Students.objects.get(admin=request.user.id)
    attendance_total=AttendanceReport.objects.filter(student_id=student_obj).count()
    attendance_present=AttendanceReport.objects.filter(student_id=student_obj,status=True).count()
    attendance_absent=AttendanceReport.objects.filter(student_id=student_obj,status=False).count()
    course=Courses.objects.get(id=student_obj.course_id.id)
    subjects=Subjects.objects.filter(course_id=course).count()

    subject_name=[]
    data_present=[]
    data_absent=[]
    subject_data=Subjects.objects.filter(course_id=student_obj.course_id)
    for subject in subject_data:
        attendance=Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=True,student_id=student_obj.id).count()
        attendance_absent_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=False,student_id=student_obj.id).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)
        return render(request,"student_template/student_home.html",{"total_attendance":attendance_total,"attendance_absent":attendance_absent,"attendance_present":attendance_present,"subjects":subjects,"data_name":subject_name,"data1":data_present,"data2":data_absent})


def student_profile_view(request):
    if request.method=='POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        address=request.POST.get('address')
        print(first_name)
        print(last_name)
        print(address)
        try:
            user=CustomUser.objects.get(id=request.user.id)
            print(user)
            student=Students.objects.get(admin=user)
            print(student)
            user.first_name=first_name
            user.last_name=last_name
            student.address=address
            user.save()
            student.save()
            messages.success(request,"Successfully Saved the details")
            return redirect('student_profile')
        except:
            messages.error(request,"Unable to save data")
            return redirect('student_profile')
    else:
        user=CustomUser.objects.get(id=request.user.id)
        student=Students.objects.get(admin=user)
    return render(request,"student_template/student_profile.html",{'user':user,'student':student})

def student_attendance_view(request):
    students=Students.objects.get(admin=request.user.id)
    course=students.course_id
    subjects=Subjects.objects.filter(course_id=course)
    return render(request,"student_template/student_attendance.html",{'subjects':subjects})

@csrf_exempt
def student_view_attendance_post(request):
    subject_id=request.POST.get("subject")
    start_date=request.POST.get("start_date")
    end_date=request.POST.get("end_date")

    start_data_parse=datetime.datetime.strptime(start_date,"%Y-%m-%d").date()
    end_data_parse=datetime.datetime.strptime(end_date,"%Y-%m-%d").date()
    subject_obj=Subjects.objects.get(id=subject_id)
    user_object=CustomUser.objects.get(id=request.user.id)
    stud_obj=Students.objects.get(admin=user_object)

    attendance=Attendance.objects.filter(attendance_date__range=(start_data_parse,end_data_parse),subject_id=subject_obj)
    attendance_reports=AttendanceReport.objects.filter(attendance_id__in=attendance,student_id=stud_obj)
    return render(request,"student_template/student_attendance_data.html",{"attendance_reports":attendance_reports})


def student_apply_leave(request):
    if request.method=='POST':
        student_id=Students.objects.get(admin=request.user.id)
        leave_date=request.POST.get('leave_date')
        leave_message=request.POST.get('reason')
        try:
            student_leave=LeaveReportStudent(student_id=student_id,leave_date=leave_date,leave_message=leave_message)
            student_leave.save()
            messages.success(request,"Successfully applied for leave!!")
            return redirect("student_apply_leave")
        except:
            messages.error(request,"unable to apply for leave!!")
            return redirect("student_apply_leave")
    else:
        student_id=Students.objects.get(admin=request.user.id)
        leave_details=LeaveReportStudent.objects.filter(student_id=student_id)
    return render(request,"student_template/student_apply_leave.html",{'leave_details':leave_details})

def student_feedback(request):
    if request.method=="POST":
        student_id=Students.objects.get(admin=request.user.id)
        feedback=request.POST.get('feedback')
        try:
            student=FeedBackStudent(student_id=student_id,feedback=feedback)
            student.save()
            messages.success(request,"FeedBack Sent Successfully!!")
            return redirect("student_feedback")
        except:
            messages.error(request,"Unable to add feedback!!")
            return redirect("student_feedback")
    else:
        student_id=Students.objects.get(admin=request.user.id)
        student_details=FeedBackStudent.objects.filter(student_id=student_id)
    return render(request,"student_template/student_feedback.html",{'student_details':student_details})

def student_grade_view(request):
    student_id=Students.objects.get(admin=request.user.id)
    student_details=StudentResult.objects.filter(student_id=student_id)
    return render(request,"student_template/student_grade.html",{'student_details':student_details})


def student_notication_view(request):
        user=request.user.id
        student_id=Students.objects.get(admin=user)
        students=NotificationStudent.objects.filter(student_id=student_id)
        return render(request,"student_template/student_notification.html",{'students':students})
