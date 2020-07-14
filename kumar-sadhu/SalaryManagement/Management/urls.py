from django.urls import path
from . import views
from django.conf.urls import url


urlpatterns = [
path("",views.home_view,name="home"),
path("home",views.home_view,name="home"),
path("logout", views.logout, name="logout"),
path("details/<str:username>",views.profile_view, name="profile"),
path("salaryselect/<str:username>", views.salaryselect_view, name="select"),
path("login",views.login_view,name="login"),
path("salarydetails/<str:username>", views.salarydetails, name = "salarydetails"),
path("changepassword", views.change_password, name = "changepassword"),
path("contactus",views.contactus, name= "contactus"),
path("timesheet/<str:username>",views.timesheet_view, name= "timesheet"),
path('pdf/<str:username>', views.gen_pdf, name="pdf"),
path('logselect/<str:username>', views.Timesheetselect_view, name = "log_select"),
path('timesheetlog/<str:username>', views.timesheetlog_view, name = "log_sheet"),
path('csv/<str:username>', views.export_csv, name = "export_csv"),
]
