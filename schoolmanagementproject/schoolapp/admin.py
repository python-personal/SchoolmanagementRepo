from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from schoolapp.models import *

class UserModel(UserAdmin):
    list_display=['id','username','email','first_name','last_name','password']

class StaffAdmin(admin.ModelAdmin):
     list_display=['id','address','admin','created_at','updated_at','fcm_token']

class CourseAdmin(admin.ModelAdmin):
    list_display=['id','course_name','created_at','updated_at']

class SubjectAdmin(admin.ModelAdmin):
    list_display=['id','subject_name','course_id','staff_id','created_at','updated_at']

class SessionYearAdmin(admin.ModelAdmin):
    list_display=['id','session_start_year','session_end_year']

class StudentAdmin(admin.ModelAdmin):
    pass
     # list_display=['id','email','first_name','last_name','username','sex','address','profile_pic']
class LeaveReportStaffAdmin(admin.ModelAdmin):
    list_display=['staff_id','leave_date','leave_message','leave_status']

class LeaveReportStudentAdmin(admin.ModelAdmin):
    list_display=['student_id','leave_date','leave_message','leave_status']

class FeedBackStaffsAdmin(admin.ModelAdmin):
    list_display=['staff_id','feedback','feedback_reply']

class StudentResultAdmin(admin.ModelAdmin):
    list_display=['id','student_id','subject_id','subject_exam_marks','subject_assignment_marks']

class AttendanceAdmin(admin.ModelAdmin):
    list_display=['id','subject_id','attendance_date']

class AttendanceReportAdmin(admin.ModelAdmin):
    list_display=['id','student_id','attendance_id','status']

class FeedBackStudentAdmin(admin.ModelAdmin):
    list_display=['id','student_id','feedback','feedback_reply']

class NotificationStudentAdmin(admin.ModelAdmin):
    list_display=['id','student_id','message','created_at']

class NotificationStaffsAdmin(admin.ModelAdmin):
    list_display=['id','staff_id','message','created_at']

admin.site.register(CustomUser,UserModel)
admin.site.register(Courses,CourseAdmin)
admin.site.register(Staffs,StaffAdmin)
admin.site.register(Subjects,SubjectAdmin)
admin.site.register(SessionYearModel,SessionYearAdmin)
admin.site.register(Students,StudentAdmin)
admin.site.register(LeaveReportStaff,LeaveReportStaffAdmin)
admin.site.register(FeedBackStaffs,FeedBackStaffsAdmin)
admin.site.register(StudentResult,StudentResultAdmin)
admin.site.register(Attendance,AttendanceAdmin)
admin.site.register(AttendanceReport,AttendanceReportAdmin)
admin.site.register(FeedBackStudent,FeedBackStudentAdmin)
admin.site.register(LeaveReportStudent,LeaveReportStudentAdmin)
admin.site.register(NotificationStaffs,NotificationStaffsAdmin)
admin.site.register(NotificationStudent,NotificationStudentAdmin)
