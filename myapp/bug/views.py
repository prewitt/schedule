# Create your views here.
#-*- coding: UTF-8 -*-
from datetime import datetime
from django.contrib import messages
from django.http import HttpResponse
from django import forms
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from app.models import Task, Staff, Group, Bug, BugComment
from app.views import valid_time, cache_on_auth
from myCalendar.views import appendSummaryBugPeriod
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
import re
class BugCommentForm(forms.ModelForm):
    content = forms.Textarea()

    class Meta:
        model = BugComment
        exclude = ('author', 'date', 'type', 'bug')

@login_required(login_url="/app/login/")
def add_bug(request):
    context = RequestContext(request)

    if request.method == 'POST':
        bug_dict = dict(request.POST.iterlists())

        bug = Bug()
        name = ""
        begin_date = ""
        end_date = ""
        state = 0
        importance = 0
        content = ""
        finish = ""
        b_task = None
        b_group = []
        b_principal = None
        b_executor = []

        if bug_dict.get("name"):
            name = bug_dict['name'][0].strip()
        if bug_dict.get("begin_date"):
            begin_date = bug_dict['begin_date'][0].strip()
        if bug_dict.get("end_date"):
            end_date = bug_dict['end_date'][0].strip()
        if bug_dict.get("state"):
            state = bug_dict['state'][0].strip()
        if bug_dict.get("importance"):
            importance = bug_dict['importance'][0].strip()
        if bug_dict.get("content"):
            content = bug_dict['content'][0].strip()
        if bug_dict.get("finish"):
            finish = bug_dict['finish'][0].strip()
        if bug_dict.get("task"):
            t_id = bug_dict['task'][0].strip()
            if t_id != '':
                b_task = Task.objects.get(id=t_id)
        if bug_dict.get("group"):
            g_ids = bug_dict['group']
            for g in g_ids:
                b_group.append(Group.objects.get(id=g))
        if bug_dict.get("principal"):
            p_id = bug_dict['principal'][0].strip()
            if p_id != '':
                b_principal = Staff.objects.get(id=p_id)
        if bug_dict.get("executor"):
            e_ids = bug_dict['executor']
            for e in e_ids:
                b_executor.append(Staff.objects.get(id=e))

        if name == '':
            messages.error(request, 'Bug名称不能为空!')
        elif re.search(r'/|\\|:|\*|<|>|\?|:|\"|\|',name):
            messages.error(request, '名称不能包含下列任何字符“ \ / : * ? " < > | ”')
        elif Task.objects.filter(name=name).count()>0:
            messages.error(request, '名称已存在！')
        elif begin_date == '':
            messages.error(request, '开始日期不能为空!')
        elif not valid_time(begin_date):
            messages.error(request, '开始日期格式不对!')
        elif end_date == '':
            messages.error(request, '结束日期不能为空!')
        elif not valid_time(end_date):
            messages.error(request, '结束日期格式不对!')
        elif content == '':
            messages.error(request, '内容不能为空!')
        elif b_principal is None:
            messages.error(request, '负责人不能为空!')
        elif b_task is None:
            messages.error(request, '所属任务不能为空!')
        else:
            bug.name = name
            bug.begin_date = begin_date
            bug.end_date = end_date
            bug.state = state
            bug.importance = importance
            bug.content = content
            bug.finish = finish
            bug.creator = request.user.staff
            bug.principal = b_principal
            bug.task = b_task
            bug.create_date = datetime.now()
            bug.save()

            for g in b_group:
                bug.group.add(g)
            for e in b_executor:
                bug.executor.add(e)

            bug.save()
            cache.clear()
            messages.success(request, '添加Bug成功!')
        tasks = Task.objects.filter(parent=None)
        group = Group.objects.all()
        ngroup = Staff.objects.filter(group=None)
        return render_to_response('bug/add_bug.html',
                                  {"tasks": tasks, "group": group, "ngroup": ngroup, 'name': name,
                                   'begin_date': begin_date, 'end_date': end_date, 'state': state, 'content': content,
                                   'importance': importance, 'finish': finish, 'b_task': b_task, 'b_group': b_group,
                                   'b_principal': b_principal, 'b_executor': b_executor}, context)
    else:
        tasks = Task.objects.filter(parent=None)
        group = Group.objects.all()
        ngroup = Staff.objects.filter(group=None)
        return render_to_response('bug/add_bug.html', {'staff': request.user.staff,
                                                       "tasks": tasks, "group": group, "ngroup": ngroup},context)

@login_required(login_url="/app/login/")
# @cache_on_auth(60*5)
def created_bug(request):
    context = RequestContext(request)
    bugs = Bug.objects.filter(creator=request.user.staff)
    comments = BugComment.objects.all()
    nf = BugCommentForm()
    return render_to_response('bug/created_bug.html',
                              {"bugs": bugs, 'comments': comments, 'nf': nf, 'staff': request.user.staff},context)

@login_required(login_url="/app/login/")
def add_comment(request, bug_id, c_type, doc):
    context = RequestContext(request)
    if request.method == 'POST':
        nf = BugCommentForm(request.POST)
        if nf.is_valid():
            nf_comment = nf.save(commit=False)
            nf_comment.bug = Bug.objects.get(id=bug_id)
            nf_comment.author = request.user.staff
            nf_comment.date = datetime.now()
            nf_comment.type = c_type
            nf_comment.save()
            cache.clear()
            return HttpResponse('提交成功')
        else:
            return HttpResponse('提交失败,内容不能为空')

    comments = BugComment.objects.all()
    nf = BugCommentForm()

    # print "doc is " + str(doc)

    if doc == '1':
        bugs = Bug.objects.filter(creator=request.user.staff)
        return render_to_response('bug/created_bug.html',
                                  {'bugs': bugs, 'comments': comments, 'nf': nf, 'staff': request.user.staff}, context)
    elif doc == '2':
        bugs = Bug.objects.filter(principal=request.user.staff)
        return render_to_response('bug/principle_bug.html',
                                  {'bugs': bugs, 'comments': comments, 'nf': nf, 'staff': request.user.staff}, context)
    elif doc == '3':
        bug = Bug.objects.get(id=bug_id)
        enablecalendar = request.user.staff.role.editCalendar
        calendar = request.user.staff.visibleCalendar.all()

        return render_to_response('bug/details_bug.html',
                                  {'bug': bug, 'comments': comments, 'nf': nf, 'staff': request.user.staff,
                                   'calendar': calendar, 'enCalendar': enablecalendar}, context)
    elif doc == '4':
        bugs = request.user.staff.b_executor.all()
        return render_to_response('bug/execute_bug.html',
                                  {'bugs': bugs, 'comments': comments, 'nf': nf, 'staff': request.user.staff}, context)
    elif doc == '5':
        bugs = Bug.objects.all
        comments = BugComment.objects.all()
        nf = BugCommentForm()
        return render_to_response('bug/all_bug.html',
                              {'bugs': bugs, 'comments': comments, 'nf': nf, 'staff': request.user.staff}, context)

@login_required(login_url="/app/login/")
def get_comments(request, bug_id):
    context = RequestContext(request)
    comments = BugComment.objects.filter(bug=bug_id)
    return render_to_response("task/get_comments.html",
        {'comments':comments})

@login_required(login_url="/app/login/")
def get_feedbacks(request, bug_id):
    context = RequestContext(request)
    comments = BugComment.objects.filter(bug=bug_id)
    return render_to_response("task/get_feedbacks.html",
        {'comments':comments})



@login_required(login_url="/app/login/")
def del_bug(request, bug_id):
    context = RequestContext(request)
    bug = Bug.objects.filter(id=bug_id)
    bug.delete()
    bugs = Bug.objects.filter(creator=request.user.staff)
    comments = BugComment.objects.all()
    nf = BugCommentForm()
    cache.clear()
    messages.success(request, "删除成功!")
    return render_to_response('bug/created_bug.html',
                              {"bugs": bugs, 'comments': comments, 'nf': nf, 'staff': request.user.staff}, context)


@login_required(login_url="/app/login/")
def add_schedule(request, bug_id, doc):
    context = RequestContext(request)
    staff_id = request.user.staff.id
    appendSummaryBugPeriod(int(staff_id), int(bug_id))
    cache.clear()
    messages.success(request, '加入日程成功')
    comments = BugComment.objects.all()
    nf = BugCommentForm()

    if doc == '1':
        bugs = Bug.objects.filter(creator=request.user.staff)
        return render_to_response('bug/created_bug.html',
                                  {'bugs': bugs, 'comments': comments, 'nf': nf, 'staff': request.user.staff}, context)
    elif doc == '2':
        bugs = Bug.objects.filter(principal=request.user.staff)
        return render_to_response('bug/principle_bug.html',
                                  {'bugs': bugs, 'comments': comments, 'nf': nf, 'staff': request.user.staff}, context)
    elif doc == '3':
        bugs = request.user.staff.b_executor.all()
        return render_to_response('bug/execute_bug.html',
                                  {'bugs': bugs, 'comments': comments, 'nf': nf, 'staff': request.user.staff}, context)


@login_required(login_url="/app/login/")
def edit_bug(request, bug_id):
    context = RequestContext(request)
    bug = Bug.objects.get(id=bug_id)
    group = Group.objects.all()
    ngroup = Staff.objects.filter(group=None)
    root_task = Task.objects.filter(parent=None)
    if request.method == "POST":
        #print "xccc"
        bug_dict = dict(request.POST.iterlists())

        bug = Bug.objects.get(id=bug_id)
        name = ""
        begin_date = ""
        end_date = ""
        state = 0
        importance = 0
        content = ""
        finish = ""
        b_task = None
        b_group = []
        b_principal = None
        b_executor = []

        if bug_dict.get("name"):
            name = bug_dict['name'][0].strip()
        if bug_dict.get("begin_date"):
            begin_date = bug_dict['begin_date'][0].strip()
        if bug_dict.get("end_date"):
            end_date = bug_dict['end_date'][0].strip()
        if bug_dict.get("state"):
            state = bug_dict['state'][0].strip()
        if bug_dict.get("importance"):
            importance = bug_dict['importance'][0].strip()
        if bug_dict.get("content"):
            content = bug_dict['content'][0].strip()
        if bug_dict.get("finish"):
            finish = bug_dict['finish'][0].strip()
        if bug_dict.get("task"):
            t_id = bug_dict['task'][0].strip()
            b_task = Task.objects.get(id=t_id)
        if bug_dict.get("group"):
            g_ids = bug_dict['group']
            for g in g_ids:
                b_group.append(Group.objects.get(id=g))
        if bug_dict.get("principal"):
            p_id = bug_dict['principal'][0].strip()
            if p_id != '':
                b_principal = Staff.objects.get(id=p_id)
        if bug_dict.get("executor"):
            e_ids = bug_dict['executor']
            for e in e_ids:
                b_executor.append(Staff.objects.get(id=e))

        if name == '':
            messages.error(request, 'Bug名称不能为空!')
        elif re.search(r'/|\\|:|\*|<|>|\?|:|\"|\|',name):
            messages.error(request, '名称不能包含下列任何字符“ \ / : * ? " < > | ”')
        elif Task.objects.filter(name=name).count()>0:
            messages.error(request, '名称已存在！')
        elif begin_date == '':
            messages.error(request, '开始日期不能为空!')
        elif not valid_time(begin_date):
            messages.error(request, '开始日期格式不对!')
        elif end_date == '':
            messages.error(request, '结束日期不能为空!')
        elif not valid_time(end_date):
            messages.error(request, '结束日期格式不对!')
        elif content == '':
            messages.error(request, '内容不能为空!')
        elif b_principal is None:
            messages.error(request, '负责人不能为空!')
        else:
            bug.name = name
            bug.begin_date = begin_date
            bug.end_date = end_date
            bug.state = state
            bug.importance = importance
            bug.content = content
            bug.finish = finish
            bug.principal = b_principal
            bug.task = b_task
            bug.save()

            bug.group.clear()
            for g in b_group:
                bug.group.add(g)

            bug.executor.clear()
            for e in b_executor:
                bug.executor.add(e)

            bug.save()
            cache.clear()
            messages.success(request, '修改成功!')
            #return redirect("/bug/created_bug/")

        return render_to_response('bug/edite_bug.html',
                                  {'staff': request.user.staff,"root_task": root_task, "bug": bug, "group": group, "ngroup": ngroup, }, context)
    else:
        return render_to_response('bug/edite_bug.html',
                                  {'staff': request.user.staff,"bug": bug, 'group': group, 'ngroup': ngroup, 'root_task': root_task},context)


@login_required(login_url="/app/login/")
# @cache_on_auth(60*5)
def details_bug(request, bug_id):
    context = RequestContext(request)
    bug = Bug.objects.get(id=bug_id)
    comments = BugComment.objects.all()
    nf = BugCommentForm()
    enablecalendar = request.user.staff.role.editCalendar
    calendar = request.user.staff.visibleCalendar.all()

    return render_to_response('bug/details_bug.html',
                              {'bug': bug, 'comments': comments, 'nf': nf, 'staff': request.user.staff,
                               'calendar': calendar, 'enCalendar': enablecalendar},context)


@login_required(login_url="/app/login/")
# @cache_on_auth(60*5)
def execute_bug(request):
    context = RequestContext(request)
    bugs = request.user.staff.b_executor.all()
    comments = BugComment.objects.all()
    nf = BugCommentForm()
    return render_to_response('bug/execute_bug.html',
                              {'bugs': bugs, 'comments': comments, 'nf': nf, 'staff': request.user.staff},context)


@login_required(login_url="/app/login/")
# @cache_on_auth(60*5)
def principal_bug(request):
    context = RequestContext(request)
    bugs = Bug.objects.filter(principal=request.user.staff)
    comments = BugComment.objects.all()
    nf = BugCommentForm()
    return render_to_response('bug/principle_bug.html',
                              {'bugs': bugs, 'comments': comments, 'nf': nf, 'staff': request.user.staff},context)


@login_required(login_url="/app/login/")
# @cache_on_auth(60*5)
def all_bug(request):
    context = RequestContext(request)
    bugs = Bug.objects.all
    comments = BugComment.objects.all()
    nf = BugCommentForm()
    return render_to_response('bug/all_bug.html',
                              {'bugs': bugs, 'comments': comments, 'nf': nf, 'staff': request.user.staff},context)


@login_required(login_url="/app/login/")
def affirm(request, bug_id):
    bug = Bug.objects.get(id=bug_id)
    bug.state = 2
    bug.save()
    bugs = Bug.objects.filter(principal=request.user.staff)
    comment = BugComment.objects.all()
    nf = BugCommentForm()
    cache.clear()
    return render_to_response('bug/principle_bug.html', {'bugs': bugs, 'comments': comment, 'nf': nf,
                                                         'staff': request.user.staff})


@login_required(login_url="/app/login/")
def submit(request, bug_id):
    bug = Bug.objects.get(id=bug_id)
    bug.state = 3
    bug.save()
    bugs = Bug.objects.filter(principal=request.user.staff)
    comment = BugComment.objects.all()
    nf = BugCommentForm()
    cache.clear()
    return render_to_response('bug/principle_bug.html', {'bugs': bugs, 'comments': comment, 'nf': nf,
                                                         'staff': request.user.staff})


@login_required(login_url="/app/login/")
def checked(request, bug_id):
    bug = Bug.objects.get(id=bug_id)
    bug.state = 4
    bug.save()
    bugs = Bug.objects.filter(creator=request.user.staff)
    comment = BugComment.objects.all()
    nf = BugCommentForm()
    cache.clear()
    return render_to_response('bug/created_bug.html', {'bugs': bugs, 'comments': comment, 'nf': nf,
                                                       'staff': request.user.staff})