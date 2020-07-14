from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group
from django.shortcuts import render, render_to_response
from Management.actions import export_as_csv_action
from django.utils.translation import ugettext_lazy
from Management.models import Desigination, Employee, Salary,TimeSheet, Department
from django.urls import path
from .forms import CsvImportForm
import csv
from datetime import datetime
from io import TextIOWrapper
import traceback

# Register your models here.

class MyAdminSite(AdminSite):

    site_title = ugettext_lazy('My site admin')


    site_header = ugettext_lazy('My administration')


    index_title = ugettext_lazy('Payroll administration')
    admin.site.site_header = "Salary Management Admin"
    admin.site.site_title = "Salary Management Admin Portal"
    admin.site.index_title = "Welcome to Salary Management Portal"
admin_site = MyAdminSite()

class TimesheetAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status')
    date_hierarchy = 'date'
    list_filter = ('employee', 'status')
    actions = [export_as_csv_action("CSV Export", fields=['employee','date','status'])]

class EmployeeAdmin(admin.ModelAdmin):
    change_list_template = "admin/Employee_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                if form.cleaned_data['csv_file']:
                     encoding = form.cleaned_data['csv_file'].charset if form.cleaned_data['csv_file'].charset else 'utf-8'
                     f = TextIOWrapper(form.cleaned_data['csv_file'].file, encoding=encoding)
                     records = csv.reader(f, dialect='excel')
                     for line in records:
                         input_data = Employee()
                         input_data.firstName = line[0]
                         input_data.lastName = line[1]
                         input_data.username = line[2]
                         input_data.password = line[3]
                         input_data.address = line[4]
                         input_data.email = line[5]
                         input_data.dob = datetime.strptime(line[6], "%m/%d/%y")
                         input_data.contact = line[7]
                         input_data.CTC = line[8]
                         input_data.department = form.cleaned_data["department"]
                         input_data.desigination = form.cleaned_data["desigination"]
                         success = True
                         message = ''
                         type1 = ''
                         try:
                             input_data.save()
                             context = {"success": success}
                         except Exception as e:
                             message = str(e)
                             type1 = str(type(e))
                             success = False

                     context = {"success": success, 'message': message, 'type': type1}
                     return render(request, 'admin/employee_success.html', context)
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, 'admin/csv_form.html', payload)




admin.site.register(Employee,EmployeeAdmin)
admin.site.register(TimeSheet,TimesheetAdmin)
admin.site.unregister(Group)
admin.site.register(Desigination)

admin.site.register(Department)
