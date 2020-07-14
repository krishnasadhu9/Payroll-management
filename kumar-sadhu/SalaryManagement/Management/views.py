from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from .models import Department, Desigination, Employee, Salary, TimeSheet
from django.contrib.auth.models import User, auth
from .forms import SalaryMonthYear,TimeSheetform
from django.contrib.auth import update_session_auth_hash
from datetime import datetime
import io
import csv
from django.http import FileResponse
from django.http import HttpResponse
from django.views.generic import View
from django.template.loader import get_template
from .utils import render_to_pdf



# Create your views here.

def login_view(request):
    if request.method== 'POST':
        username1 = request.POST['username']
        password1 = request.POST['password']


        if Employee.objects.filter(username=username1).exists():
            if User.objects.filter(username=username1).exists():
                user = auth.authenticate(username=username1,password=password1)
            else:
                x = Employee.objects.get(username = username1)
                if x.username == username1:
                    first_name = x.firstName
                    last_name = x.lastName
                    username = x.username
                    password = x.password
                    password2 = x.password
                    email = x.email
                    user = User.objects.create_user(username=username, password=password, email=email,first_name=first_name,last_name=last_name)
                    user.save();
        else:
            messages.info(request,'Invalid Credentials')
            return redirect('login')

        if Employee.objects.filter(username=username1).exists():
            user = auth.authenticate(username=username1,password=password1)
        else:
            user = None

        if user is not None:
            auth.login(request, user)
            x = user.username
            return redirect('home')
        else:
            messages.info(request,'Invalid Credentials')
            return redirect('login')
    else:
        return render(request,'Management/login.html')


def logout(request):
    auth.logout(request)
    return redirect('login')


def change_password(request):
    if request.method == 'POST':
        username = request.POST["username"]
        currentpassword = request.POST['currentpassword']
        newpassword = request.POST['newpassword']

        employee = Employee.objects.get(username = username)
        user = User.objects.get(username=username)

        if username == user.username:
            if currentpassword == employee.password:
                user.password = newpassword
                user.save();
                update_session_auth_hash(request, user)

                employee.password = newpassword
                employee.save();
                return redirect('home')

            else:
                messages.info(request,'Current password Is Invalid')
                return redirect('changepassword')
        else:
            messages.info(request,'User name does not exist')
            return redirect('changepassword')
    else:
        return render(request, 'Management/changepassword.html')

def home_view(request):
    return render(request, 'Management/home.html')


def contactus(request):
    if request.method == "POST":
        sub = "Details submitted successfully! will be in touch ! "
        return render(request, 'Management/contactus.html', {'sub': sub})

    return render(request, 'Management/contactus.html')

def timesheet_view(request, username):
    for x in Employee.objects.all():
        if x.username == username:
            employee = x

    if request.method == "POST":
        status = request.POST['leave']
        datepicker = request.POST['datepicker']
        datepicker = datetime.strptime(datepicker, "%m/%d/%Y").strftime('%Y-%m-%d')
        employee_filter= Employee.objects.filter(username = username)
        employee_exist = TimeSheet.objects.filter(employee__in = employee_filter).filter(date = datepicker)
        date = datetime.strptime(datepicker, "%Y-%m-%d")
        if len(employee_exist) == 0:
            TimeSheet(employee = employee, status = status, date = datepicker).save()
            salary_exist = Salary.objects.filter(employee__in = employee_filter).filter(salaryMonth = str(date.month)).filter(salaryyear = date.year)
            if len(salary_exist) == 0:
                if status != 'unpaid':
                    Salary(employee =employee, salaryMonth = date.month, salaryyear = date.year, working_days = workingdays(date.month), working_days_worked = 1, other_allowances= '800').save()
                    sub = "submitted succesfully"
                else:
                    Salary(employee =employee, salaryMonth = date.month, salaryyear = date.year, working_days = workingdays(date.month), working_days_worked = 0, other_allowances= '800').save()
                    sub = "submitted succesfully"
            else:
                for employee_salary in salary_exist:
                    if status != 'unpaid':
                        employee_salary.working_days_worked = employee_salary.working_days_worked + 1
                        employee_salary.save()
                        sub = "submitted succesfully"
        else:
            sub = "Time sheet on " + "  " + datepicker + " " + "is already submitted as" + "   " + status
            return render(request, 'Management/timesheet.html', {"employee": employee, "sub": sub})
    return render(request, 'Management/timesheet.html', {"employee": employee})

def workingdays(salaryMonth):
    if salaryMonth == 1:
        return 31
    if salaryMonth == 2:
        return 28
    if salaryMonth == 3:
        return 31
    if salaryMonth == 4:
        return 30
    if salaryMonth == 5:
        return 31
    if salaryMonth == 6:
        return 30
    if salaryMonth == 7:
        return 31
    if salaryMonth == 8:
        return 31
    if salaryMonth == 9:
        return 30
    if salaryMonth == 10:
        return 31
    if salaryMonth == 12:
        return 31
    if salaryMonth == 11:
        return 30


def salarydetails(request, username):
    for x in Employee.objects.all():
        if x.username == username:
            employee = x

    if request.method == "POST":
        salaryform = SalaryMonthYear(request.POST)
    else:
        salaryform = SalaryMonthYear()

    salitem = ''
    for x in Salary.objects.all():
        if x.employee.username == employee.username and salaryform.data['year'] == str(x.salaryyear) and salaryform.data[
            'month'] == x.salaryMonth:
            salitem = x
            salitem.salary_calculation()
            break

    return render(request, 'Management/salarydetails.html',
                  {"salaryform": salaryform, "salitem": salitem, "employee": employee})

def salaryselect_view(request, username):
    years = []
    months= []
    for employee in Employee.objects.all():
        if employee.username == username:
            profile = employee
    for salary in Salary.objects.all():
        if salary.employee == profile:
            if salary.salaryMonth not in months:
                months.append(salary.salaryMonth)
            if salary.salaryyear not in years:
                years.append(salary.salaryyear)

    context = {'employee': profile, 'months' : months , 'years' : years}
    return render(request, 'Management/salaryselect.html', context)

def Timesheetselect_view(request, username):
    years = []
    months= []
    for employee in Employee.objects.all():
        if employee.username == username:
            profile = employee
    for salary in Salary.objects.all():
        if salary.employee == profile:
            if salary.salaryMonth not in months:
                months.append(salary.salaryMonth)
            if salary.salaryyear not in years:
                years.append(salary.salaryyear)

    context = {'employee': profile, 'months' : months , 'years' : years}
    return render(request, 'Management/timesheetselect.html', context)

def timesheetlog_view(request, username):
    if request.method == "POST":
        context = {}
        month = request.POST['month']
        year = request.POST['year']
        employee_filter= Employee.objects.filter(username = username)
        Timesheetlog = TimeSheet.objects.filter(employee__in = employee_filter).filter(date__month = str(month)).filter(date__year = str(year))
        return render(request,'Management/timesheetlog.html', {"Timesheetlog":Timesheetlog})

def export_csv(request, username):
    if request.method == "POST":
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; sfilename="users.csv"'
        writer = csv.writer(response)
        writer.writerow(['Date', 'status'])
        month = request.POST['month']
        year = request.POST['year']
        employee_filter= Employee.objects.filter(username = username)
        Timesheetlog = TimeSheet.objects.filter(employee__in = employee_filter).filter(date__month = str(month)).filter(date__year = str(year)).values_list('date', 'status')
        for x in Timesheetlog:
            writer.writerow(x)
        return response


def get_month(salaryMonth):
    if salaryMonth == 1:
        return 'January'
    if salaryMonth == 2:
        return 'February'
    if salaryMonth == 3:
        return 'March'
    if salaryMonth == 4:
        return 'April'
    if salaryMonth == 5:
        return 'May'
    if salaryMonth == 6:
        return 'June'
    if salaryMonth == 7:
        return 'July'
    if salaryMonth == 8:
        return 'August'
    if salaryMonth == 9:
        return 'September'
    if salaryMonth == 10:
        return 'October'
    if salaryMonth == 12:
        return 'December'
    if salaryMonth == 11:
        return 'November'


def salarydetails_view(request):
    return render(request,'Management/salarydetails.html')

def profile_view(request, username):
    for employee in Employee.objects.all():
        if employee.username == username:
            employee1 = employee
    context = {'employee': employee1}
    return render(request, 'Management/employee_details.html', context)

def gen_pdf(request, username):
    if request.method == "POST":
        employee_filter= Employee.objects.filter(username = username)
        salitem = Salary.objects.filter(employee__in = employee_filter).filter(salaryyear = request.POST['year']).filter(salaryMonth = request.POST[
            'month'])
        for x in salitem:
            x.salary_calculation()
            sal = {"firstName": x.employee.firstName, "lastName": x.employee.lastName, "contact": x.employee.contact,
                     "email" : x.employee.email, "department": x.employee.department, "desigination": x.employee.desigination,
                     "CTC" : x.CTC, "Monthly_salary" : x.Monthly_salary, "basic_salary":x.basic_salary, "da_salary":x.da_salary ,
                     "hra_salary" : x.hra_salary , "ca_salary": x.ca_salary , "other_allowances" :x.other_allowances , "total_earning" : x.total_earning,
                     "pf_salary" : x.pf_salary , "pt_salary":x.pt_salary, "td_salary":x.td_salary,"total_deductions":x.total_deductions,
                     "total":x.total, "no_of_days_leave" : x.no_of_days_leave, "amount_to_deduct_for_leave":x.amount_to_deduct_for_leave,
                     "working_days" : x.working_days, "nettotal": x.nettotal,
                     "salaryMonth": x.salaryMonth, "salaryyear": x.salaryyear}

        context = {'salitem' :sal, 'request':request}
        return render_to_pdf('Management/pdf.html',context)
