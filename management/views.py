import calendar
import pytz
import decimal
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import RequestForm, AddProjectForm, AssignEmployeeForm
from .models import Requests
from accounts.models import Account, Payroll
from projects.models import WorkDiary, Project, ProjectAssignment
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.defaultfilters import slugify
from accounts.models import Account, Payroll
from projects.models import WorkDiary, Project, ProjectAssignment
from datetime import datetime, timedelta
from threading import Timer
from .forms import RequestForm, AddProjectForm, AssignEmployeeForm
from .models import Requests
from .pdf import CreatePdf
from .utils import DateUtils, ProjectsUtils

# Create your views here.


class RequestView(TemplateView):
    template_name = 'management/request.html'

    def get(self, request, *args, **kwargs):
        form = RequestForm(initial={'employee': request.user.id})
        requests_by_user = Requests.objects.filter(
            employee=request.user.id).order_by('-date_requested')
        return_data = {'form': form, 'requests_by_user': requests_by_user}
        return render(request, self.template_name, return_data)

    def post(self, request, *args, **kwargs):
        form = RequestForm(request.POST)
        if form.is_valid():
            form.save()
            form = RequestForm()
            requests_by_user = Requests.objects.filter(
                employee=request.user.id)
        return redirect('request')


class UpdateRequest(TemplateView):

    def post(self, request, *args, **kwargs):
        id = request.POST['id']
        status = request.POST['status']
        confirmed = status or None
        Requests.objects.filter(id=id).update(confirmed=confirmed)
        # subject = 'Request for leave confirmation'
        # messages = 'Your request for leave with subject '+request.POST['subject']+' and content '+request.POST['content']+' was confirmed'
        # from_email = settings.EMAIL_HOST_USER
        return redirect('view_all_requests')


class AdminView(TemplateView):
    template_name = 'management/workdiaries.html'

    def get(self, request, *args, **kwargs):
        projects = Project.objects.all()
        day_diff = int(kwargs['day'])
        date_today = datetime.now() - timedelta(days=day_diff)
        previous_day = day_diff + 1
        if day_diff is 0:
            next_day = 0
        else:
            next_day = day_diff - 1
        '''
        Add __date to the datefield to use only the date of the datetime object in the query
        '''
        work_diaries = WorkDiary.objects.filter(
            date__date=date_today).order_by('-date')
        return_data = {'projects': projects, 'work_diaries': work_diaries,
                       'date_now': date_today, 'previous_day': previous_day, 'next_day': next_day}
        return render(request, self.template_name, return_data)

    def post(self, request, *args, **kwargs):
        day_diff = int(kwargs['day'])
        previous_day = day_diff + 1
        if day_diff is 0:
            next_day = 0
        else:
            next_day = day_diff - 1
        the_date = request.POST.get('getDiariesByDate')
        the_date = datetime.strptime(the_date, '%m/%d/%Y')
        work_diaries = WorkDiary.objects.filter(date__date=the_date)
        return_data = {'work_diaries': work_diaries, 'previous_day': previous_day,
                       'next_day': next_day, 'date_now': the_date, 'return_today': True}
        return render(request, self.template_name, return_data)


class ConfirmAccountView(TemplateView):

    def post(self, request, *args, **kwargs):
        if request.POST.get('confirm') is not None:
            employee = request.POST['id']
            Account.objects.filter(id=employee).update(is_active=True)
            return redirect('all_employees')
        if request.POST.get('decline') is not None:
            employee = request.POST['id']
            account = Account.objects.get(id=employee)
            account.delete()
            return redirect('all_employees')


class DeactivateAccountView(TemplateView):

    def post(self, request, *args, **kwargs):
        employee = request.POST['id']
        Account.objects.filter(id=employee).update(is_active=False)
        return redirect('admin', day=0)


class AllEmployeesView(TemplateView):
    template_name = 'management/employees.html'

    def get(self, request, *args, **kwargs):
        all_employees = Account.objects.filter(is_active=True)
        projects = Project.objects.all()
        accounts_to_confirm = Account.objects.filter(is_active=False)
        return_data = {'all_employees': all_employees,
                       'accounts_to_confirm': accounts_to_confirm, 'projects': projects}
        return render(request, self.template_name, return_data)


class EmployeeProfileView(TemplateView):
    template_name = 'management/employee-profile.html'

    def get(self, request, *args, **kwargs):
        employee_id = kwargs['id']
        employee = Account.objects.get(id=employee_id)
        projects = Project.objects.all()
        return_data = {'employee': employee, 'projects': projects}
        return render(request, self.template_name, return_data)


class ViewRequestsView(TemplateView):
    template_name = 'management/all-requests.html'

    def get(self, request, *args, **kwargs):
        all_requests = Requests.objects.all()
        projects = Project.objects.all()
        return_data = {'all_requests': all_requests, 'projects': projects}
        return render(request, self.template_name, return_data)


class ProjectManageView(TemplateView):

    template_name = 'management/project.html'

    def get(self, request, *args, **kwargs):

        project = Project.objects.get(id=kwargs.get('id'))
        assignment = ProjectAssignment.objects.filter(project=project)
        works = WorkDiary.objects.filter(project_assignment=assignment).order_by('-date')
        page = self.request.GET.get('page', 1)
        paginator = Paginator(works, 5)
        try:
            works = paginator.page(page)
        except PageNotAnInteger:
            works = paginator.page(1)
        except EmptyPage:
            works = paginator.page(paginator.num_pages)
        ctx_data = {
            'works': works,
            'project': project,
        }
        return render(request, self.template_name, ctx_data)


class ViewReportsByEmployee(TemplateView):

    template_name = 'management/reports_by_employee.html'

    def get(self, request, *args, **kwargs):

        emp_id = kwargs['emp_id']
        emp = Account.objects.get(id=emp_id)
        project_assignments = ProjectAssignment.objects.filter(employee=emp_id)
        page = self.request.GET.get('page', 1)
        paginator = Paginator(project_assignments, 5)
        try:
            project_assignments = paginator.page(page)
        except PageNotAnInteger:
            project_assignments = paginator.page(1)
        except EmptyPage:
            project_assignments = paginator.page(paginator.num_pages)
        projects = []
        for project in project_assignments:
            projects.append(project.id)
        reports = WorkDiary.objects.filter(project_assignment__in=projects).order_by('-date')
        return_data = {'reports': reports, 'employee': emp,
                       'project_assignments': project_assignments, }
        return render(request, self.template_name, return_data)


class ManagementPayrollView(TemplateView):
    template_name = 'management/payroll.html'

    def get(self, request, *args, **kwargs):
        '''
        1. Create payroll record
        '''
        date_now = datetime.now(pytz.utc)
        du = DateUtils()
        date_sep = du.get_year_month_day(date_now)
        d, m, y = date_sep['get_day'], date_sep['get_month'], date_sep['get_year']
        last_day = calendar.monthrange(y, m)[1]
        employees = Account.objects.all().exclude(is_staff=True)
        if d is 15 or d is last_day:
            has_date = Payroll.objects.filter(date__date=date_now.date()).exists()
            if has_date is True:
                pass
            else:
                for emp in employees:
                    '''
                    2. Get total hours of employee for the period and generate the invoice
                    '''
                    pu = ProjectsUtils()
                    projects = pu.get_employee_projects_assignments(emp.id)
                    date_from = du.get_start_date(date_now)
                    diaries = WorkDiary.objects.filter(
                        project_assignment__in=projects, date__date__gte=date_from, date__date__lte=date_now)
                    total_hours = decimal.Decimal(0.00)
                    for d in diaries:
                        total_hours = total_hours + decimal.Decimal(d.hours)
                    '''
                    3. Get payroll record and generate the invoice
                    '''
                    AMOUNT_BEFORE_DEDUCTIONS = total_hours * emp.hourly_rate
                    PAYROLL_DESCRIPTION = 'Salary for the month'
                    # Prepare requirements for pdf creation
                    data = {'fname': emp.first_name, 'lname': emp.last_name,  'amount': AMOUNT_BEFORE_DEDUCTIONS,
                            'description': PAYROLL_DESCRIPTION, 'period': date_now.date(), 'total_hours': total_hours}
                    template = 'management/payroll-report.html'
                    file_path = 'payroll/' + \
                        slugify(emp.first_name + '_' + emp.last_name +
                                '_' + str(date_now.date())) + '.pdf'
                    style = 'h3 {font-size: 18px; font-weight: bold; text-align: center}' + \
                        'h4 {font-size: 16px; font-weight: bold}'
                    cp = CreatePdf()
                    payroll_report = cp.generate_pdf(data, template, file_path, style)
                    '''
                    Save payroll record
                    '''
                    p = Payroll(
                        date=date_now,
                        employee=emp,
                        amount_before_deductions=AMOUNT_BEFORE_DEDUCTIONS,
                        description=PAYROLL_DESCRIPTION,
                        paid=False,
                        invoice_file=file_path
                    )
                    p.save()
        '''
        Now return the payroll records
        '''
        payrolls = Payroll.objects.all()
        return_data = {'payrolls': payrolls}
        return render(request, self.template_name, return_data)

    def post(self, request, *args, **kwargs):
        pay_id = request.POST['id']
        status = request.POST['status']
        invoice_file = request.POST['invoice_file']
        paid = status
        Payroll.objects.filter(id=pay_id).update(paid=paid, date_paid=datetime.now(pytz.utc))
        '''
        Send an email to the employee after confirming the payroll
        '''
        message = EmailMessage(
            'Payroll confirmation',
            'Hi! Your payroll is successfully confirmed! You may view or download it from the attachment. Thank you.',
            'gergimarjohnalinsangao@gmail.com',
            ['fantanhoj_ramiger@ymail.com']
        )
        message.attach_file('media/' + invoice_file)
        message.send()
        return redirect('management_payroll')


class AddProjectView(TemplateView):

    form_class = AddProjectForm
    template_name = 'management/project-add.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial={'user': request.user.id})
        ctx_data = {
            'form': form,
        }
        return render(request, self.template_name, ctx_data)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            p = form.save()
            return redirect('view_projects', id=p.id)
        ctx_data = {
            'form': form,
            'error': 'Can\'t add project',
        }
        return render(request, self.template_name, ctx_data)


class AssignEmployeeView(TemplateView):

    form_class = AssignEmployeeForm
    template = 'management/project-assign-employee.html'

    def get(self, request, *args, **kwargs):
        proj_id = kwargs['id']
        form = self.form_class(initial={'project': proj_id})
        ctx_data = {
            'form': form,
            'proj_id': proj_id,
        }
        return render(request, 'management/project-assign-employee.html', ctx_data)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            employee = request.POST.get('employee')
            project = request.POST.get('project')
            assigned = ProjectAssignment.objects.filter(
                employee=employee, project=project).exists()
            if assigned is True:
                error = 'Employee is already assigned to this project.'
            else:
                p_id = form.save()
                return redirect('view_projects', id=p_id.id)
        ctx_data = {
            'form': form,
            'error': error,
        }
        return render(request, 'management/project-assign-employee.html', ctx_data)
