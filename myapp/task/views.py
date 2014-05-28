#-*- coding: UTF-8 -*-
# Create your views here.
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from mptt.models import MPTTModel
from app.models import Task, Comment, Group, Staff
from django import forms
from django.http import HttpResponse
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.views import permission_required_with, valid_time, cache_on_auth
from django.template import Template, Context
from django.db.models import Q
from myCalendar.views import updateSummary
from django.views.decorators.cache import cache_page
from django.http import HttpResponseRedirect
from django.core.cache import cache
import re


class CommentForm(forms.ModelForm):
    content = forms.Textarea()

    class Meta:
        model = Comment
        exclude = ('author', 'date', 'type', 'task')


@login_required(login_url="/app/login/")
def add_task(request):
    context = RequestContext(request)

    edit_task = request.user.staff.role.editTask
    global g_parent_add
    if request.method == 'POST':

        my_dict = dict(request.POST.iterlists())

        name = my_dict['name'][0].strip()
        create_date = datetime.now()
        begin_date = request.POST.get('begin_date')
        end_date = request.POST.get('end_date')
        state = my_dict['state'][0].strip()
        importance = my_dict['importance'][0].strip()
        content = my_dict['content'][0].strip()
        finish = my_dict['finish'][0].strip()

        principal = None
        if my_dict.get('principal'):
            did = my_dict['principal'][0].strip()
            if did != '' and did != 0 and did != 'undefined':
                principal = Staff.objects.get(id=did)

        t_parent = None
        parent_v = []
        if my_dict.get('parent'):
            pid = my_dict['parent'][0].strip()
            if pid != 'None' and pid != '-1' and pid != 0:
                t_parent = Task.objects.get(id=pid)
                tmp_t = t_parent
                while tmp_t is not None:
                    parent_v.append(tmp_t.creator)
                    parent_v.append(tmp_t.principal)
                    tmp_t = tmp_t.parent
        else:
            pid = 0

        t_group = []
        if my_dict.get('group'):
            tmp_group = my_dict['group']
            for tg in tmp_group:
                t_group.append(Group.objects.get(id=tg))

        executor = []
        if my_dict.get("executor"):
            tmp_exe = my_dict["executor"]
            for e in tmp_exe:
                executor.append(Staff.objects.get(id=e))

        visible = []
        if my_dict.get("visible"):
            tmp_visible = my_dict["visible"]
            for v in tmp_visible:
                visible.append(Staff.objects.get(id=v))
        if name == '':
            messages.error(request, '名称不能为空！')
        elif re.search(r'/|\\|:|\*|<|>|\?|:|\"|\|', name):
            messages.error(request, '名称不能包含下列任何字符“ \ / : * ? " < > | ”')
        elif t_parent == None and Task.objects.filter(name=name, mptt_level=0, istemp=0).count() > 0:
            messages.error(request, '名称已存在！')
        elif begin_date == '' or end_date == '':
            messages.error(request, '开始日期和结束日期不能为空！')
        elif content == '':
            messages.error(request, '任务内容不能为空！')
        elif principal is None:
            messages.error(request, '负责人不能为空！')
        elif (not edit_task and pid == 0) or pid == '-1':
            messages.error(request, '您没有权限创建该任务！')
        elif not valid_time(begin_date):
            messages.error(request, '开始日期格式错误！')
        elif not valid_time(end_date):
            messages.error(request, '结束日期格式错误！')
        else:
            tsk = Task()
            tsk.name = name
            tsk.create_date = create_date
            tsk.begin_date = begin_date
            tsk.end_date = end_date
            tsk.state = state
            tsk.importance = importance
            tsk.content = content
            ff = finish
            if len(ff) > 50:
                finish = ff[0:49]
            tsk.finish = finish
            tsk.parent = t_parent
            tsk.creator = request.user.staff
            tsk.principal = principal

            tsk.save()

            tsk.group.clear()
            for g in t_group:
                tsk.group.add(g)

            tsk.executor.clear()
            for e in executor:
                tsk.executor.add(e)

            tsk.viewing.clear()
            tsk.viewing.add(request.user.staff)
            tsk.viewing.add(principal)

            for v in visible:
                if not tsk.viewing.filter(id=v.id):
                    tsk.viewing.add(v)

            for e in executor:
                if not tsk.viewing.filter(id=e.id):
                    tsk.viewing.add(e)
            for tp in parent_v:
                if not tsk.viewing.filter(id=tp.id):
                    tsk.viewing.add(tp)
            # cache.clear()
            messages.success(request, "创建任务成功!")
            if my_dict.get('temp'):
                temp_id = my_dict['temp'][0].strip()
                if temp_id != '-1':
                    createTaskBy(request, temp_id, tsk.id)

                    #parent = Task.objects.all()
        staff = Staff.objects.filter(visible=True)
        group = Group.objects.all()
        ngroup = Staff.objects.filter(group=None)
        temps = Task.objects.filter(Q(istemp=1) & Q(parent=None))
        return render_to_response('task/add_task.html',
                                  {'parent': g_parent_add, 'staff': request.user.staff, 'group': group,
                                   'ngroup': ngroup,
                                   't_name': name, 't_begin_date': begin_date, 't_end_data': end_date, 't_state': state,
                                   't_importance': importance, 't_content': content, 't_finish': finish,
                                   't_principal': principal, 't_parent': t_parent, 't_group': t_group, 'temps': temps,
                                   't_executor': executor, 't_visible': visible, 'edit_task': edit_task}, context)
    else:

        p_parent = []
        task_execute = request.user.staff.task
        task_cp = Task.objects.filter(
            Q(istemp=False) & (Q(creator=request.user.staff) | Q(principal=request.user.staff)))
        task_viewing = request.user.staff.viewing.all()
        for t1 in task_execute.all():
            has = False
            for p in p_parent:
                if p == t1:
                    has = True
                    break
            if not has:
                p_parent.append(t1)

        for t2 in task_cp:
            has = False
            for p in p_parent:
                if p == t2:
                    has = True
                    break
            if not has:
                p_parent.append(t2)
        for t3 in task_viewing:
            p_parent.append(t3)
        g_parent_add = Task.objects.filter(istemp=0)
        for p in g_parent_add:
            has = False
            for t1 in p_parent:
                if p == t1:
                    has = True
                    break
            if not has:
                p.name = "没有权限的项目"
                p.id = -1

        staff = Staff.objects.filter(visible=True)
        group = Group.objects.all()
        ngroup = Staff.objects.filter(group=None)
        temps = Task.objects.filter(Q(istemp=1) & Q(parent=None))
        return render_to_response('task/add_task.html',
                                  {'parent': g_parent_add, 'staff': request.user.staff, 'group': group,
                                   'edit_task': edit_task, 'ngroup': ngroup, 'temps': temps}, context)


@login_required(login_url="/app/login/")
# @cache_on_auth(60 * 5)
def created_task(request):
    context = RequestContext(request)
    tasks = Task.objects.filter(Q(istemp=0) & Q(creator=request.user.staff))

    comment = Comment.objects.all()
    nf = CommentForm()

    return render_to_response('task/created_task.html',
                              {'tasks': tasks, 'comments': comment, 'nf': nf, 'staff': request.user.staff}, context)


@login_required(login_url="/app/login/")
#@permission_required_with('task')
# @cache_on_auth(60 * 5)
def doing_task(request):
    context = RequestContext(request)
    tasks = Task.objects.filter(Q(principal=request.user.staff) & Q(istemp=0))
    comment = Comment.objects.all()
    nf = CommentForm()
    return render_to_response('task/doing_task.html', {'tasks': tasks, 'comments': comment, 'nf': nf,
                                                       'staff': request.user.staff}, context)


@login_required(login_url="/app/login/")
# @cache_on_auth(60 * 5)
#@permission_required_with('task')
def executed_task(request):
    context = RequestContext(request)
    tasks = request.user.staff.task.filter(istemp=0)
    comment = Comment.objects.all()
    nf = CommentForm()
    return render_to_response('task/executed_task.html', {'tasks': tasks, 'comments': comment, 'nf': nf,
                                                          'staff': request.user.staff}, context)


@login_required(login_url="/app/login/")
# @cache_on_auth(60 * 5)
def show_task(request):
    context = RequestContext(request)
    edit_task = request.user.staff.role.editTask
    tasks = Task.objects.filter(istemp=0).order_by("-begin_date")
    #tasks = Task.objects.all()
    usr = request.user
    map_task = {}

    for t in tasks:
        # print t.create_date
        map_task[t.id] = 2
        for v in t.viewing.all():
            if v.id == usr.staff.id:
                map_task[t.id] = 1
                break
    return render_to_response('task/task.html', {'tasks': tasks, 'staff': request.user.staff, 'map_task': map_task,
                                                 'edit_task': edit_task}, context)


@login_required(login_url="/app/login/")
#@permission_required_with('task')
# @cache_on_auth(60 * 15)
def all_task(request):
    context = RequestContext(request)
    usr = request.user
    tasks = usr.staff.viewing.all()
    comment = Comment.objects.all()
    nf = CommentForm()
    return render_to_response('task/all_task.html',
                              {'tasks': tasks, 'comments': comment, 'nf': nf, 'staff': request.user.staff}, context)


def getPath(task_id):
    task = Task.objects.get(id=task_id)

    parent = task.parent
    namepath = []
    namepath.append(task.name)
    while parent is not None:
        namepath.append(parent.name)
        tp = parent
        parent = tp.parent

    path = ''
    while len(namepath) > 0:
        path = path + '/' + namepath.pop()

    return path + '/'


@login_required(login_url="/app/login/")
#@permission_required_with('task')
def show_detail(request, my_id):
    context = RequestContext(request)
    task = Task.objects.get(id=my_id)
    comment = Comment.objects.all()
    nf = CommentForm()
    enablecalendar = request.user.staff.role.editCalendar
    calendar = request.user.staff.visibleCalendar.all()

    taskpath = getPath(my_id)
    return render_to_response('task/task_details.html',
                              {'task': task, 'comments': comment, 'nf': nf, 'staff': request.user.staff,
                               'calendar': calendar, 'enCalendar': enablecalendar, 'taskPath': taskpath}, context)


@login_required(login_url="/app/login/")
#@permission_required_with('task')
# @cache_on_auth(60 * 5)
def comments(request, task_id, c_type):
    context = RequestContext(request)
    global t_id
    global t_type
    if request.method == 'POST':
        nf = CommentForm(request.POST)
        if nf.is_valid():
            nf_comment = nf.save(commit=False)
            nf_comment.task = Task.objects.get(id=t_id)
            nf_comment.author = request.user
            nf_comment.date = datetime.datetime.now()
            nf_comment.type = t_type
            nf_comment.save()
            # cache.clear()
            return HttpResponse("发表成功")
        else:
            return HttpResponse("请填写内容....")
    else:
        t_id = task_id
        t_type = c_type
        comment = CommentForm()
        return render_to_response('task/doing_task.html', {'staff': request.user.staff, 'comments': comment}, context)

@login_required(login_url="/app/login/")
def get_comments(request, task_id):
    context = RequestContext(request)
    comments = Comment.objects.filter(task=task_id)
    # print "comments"+task_id
    return render_to_response("task/get_comments.html",
        {'comments':comments})

@login_required(login_url="/app/login/")
def get_feedbacks(request, task_id):
    context = RequestContext(request)
    comments = Comment.objects.filter(task=task_id)
    # print "comments"+task_id
    return render_to_response("task/get_feedbacks.html",
        {'comments':comments})

@login_required(login_url="/app/login/")
#@permission_required_with('task')
def delete(request, task_id):
    context = RequestContext(request)
    task = Task.objects.filter(id=task_id)

    task.delete()

    tasks = Task.objects.filter(Q(creator=request.user.staff) & Q(istemp=0))

    comment = Comment.objects.all()
    nf = CommentForm()
    # cache.clear()
    messages.success(request, '删除任务成功！')
    return render_to_response('task/created_task.html',
                              {'tasks': tasks, 'comments': comment, 'nf': nf, 'staff': request.user.staff}, context)


@login_required(login_url="/app/login/")
#@permission_required_with('task')
def deleteTree(request, task_id):
    context = RequestContext(request)
    task = Task.objects.filter(id=task_id)
    task.delete()

    edit_task = request.user.staff.role.editTask
    tasks = Task.objects.filter(istemp=0)
    #tasks = Task.objects.all()
    usr = request.user
    map_task = {}
    for t in tasks:
        map_task[t.id] = 2
        for v in t.viewing.all():
            if v.id == usr.staff.id:
                map_task[t.id] = 1
                break
    # cache.clear()
    messages.success(request, '删除任务成功！')
    #return HttpResponseRedirect("/task/show_task/")
    return render_to_response('task/task.html', {'tasks': tasks, 'staff': request.user.staff, 'map_task': map_task,
                                                 'edit_task': edit_task}, context)


@login_required(login_url="/app/login/")
#@permission_required_with('task')
def checked(request, task_id):
    context = RequestContext(request)
    task = Task.objects.get(id=task_id)
    task.state = 4
    task.save()
    # cache.clear()
    tasks = Task.objects.filter(Q(creator=request.user.staff) & Q(istemp=0))
    comment = Comment.objects.all()
    nf = CommentForm()
    messages.success(request, '修改成功！')
    return render_to_response('task/created_task.html',
                              {'tasks': tasks, 'comments': comment, 'nf': nf, 'staff': request.user.staff}, context)


@login_required(login_url="/app/login/")
#@permission_required_with('task')
def affirm(request, task_id):
    task = Task.objects.get(id=task_id)
    task.state = 2
    task.save()
    # cache.clear()
    tasks = Task.objects.filter(Q(principal=request.user.staff) & Q(istemp=0))
    comment = Comment.objects.all()
    nf = CommentForm()
    return render_to_response('task/doing_task.html', {'tasks': tasks, 'comments': comment, 'nf': nf,
                                                       'staff': request.user.staff})


@login_required(login_url="/app/login/")
#@permission_required_with('task')
def submit(request, task_id):
    task = Task.objects.get(id=task_id)
    task.state = 3
    task.save()
    # cache.clear()
    tasks = Task.objects.filter(Q(principal=request.user.staff) & Q(istemp=0))
    comment = Comment.objects.all()
    nf = CommentForm()
    return render_to_response('task/doing_task.html', {'tasks': tasks, 'comments': comment, 'nf': nf,
                                                       'staff': request.user.staff})


@login_required(login_url="/app/login/")
#@permission_required_with('task')
def modify(request, task_id):
    context = RequestContext(request)
    edit_task = request.user.staff.role.editTask
    if request.method == "POST":
        my_dict = dict(request.POST.iterlists())
        name = my_dict['name'][0].strip()
        begin_date = my_dict['begin_date'][0].strip()
        end_date = my_dict['end_date'][0].strip()

        state = my_dict['state'][0].strip()
        importance = my_dict['importance'][0].strip()
        parent = my_dict['parent'][0].strip()
        principal = my_dict['principal'][0].strip()
        content = my_dict['content'][0].strip()
        finish = my_dict['finish'][0].strip()
        group = []
        if my_dict.get('group'):
            group = my_dict['group']

        if name == '':
            messages.error(request, '名称不能为空！')
        elif re.search(r'/|\\|:|\*|<|>|\?|:|\"|\|', name):
            messages.error(request, '名称不能包含下列任何字符“ \ / : * ? " < > | ”')
        elif parent == None and Task.objects.filter(name=name, mptt_level=0, istemp=0).count() > 0:
            messages.error(request, '名称已存在！')
        elif begin_date == '' or end_date == '':
            messages.error(request, '开始日期和结束日期不能为空！')
        elif content == '':
            messages.error(request, '任务内容不能为空！')
        elif principal is None:
            messages.error(request, '负责人不能为空！')
        elif not valid_time(begin_date):
            messages.error(request, '开始日期格式错误！')
        elif not valid_time(end_date):
            messages.error(request, '结束日期格式错误！')
        else:
            m_task = Task.objects.get(id=task_id)

            principal = Staff.objects.get(id=principal)

            m_task.group = group

            m_task.viewing.clear()
            if my_dict.get('visible'):
                visible = my_dict['visible']
                for v in visible:
                    #vo = Staff.objects.get(id=v)
                    if not m_task.viewing.filter(id=v):
                        m_task.viewing.add(v)

            m_task.executor.clear()
            if my_dict.get('executor'):
                executor = my_dict['executor']
                for e in executor:
                    m_task.executor.add(e)
                    if not m_task.viewing.filter(id=e):
                        m_task.viewing.add(e)
            tmp_p = m_task.parent
            while tmp_p is not None:
                if not m_task.viewing.filter(id=tmp_p.creator.id):
                    m_task.viewing.add(tmp_p.creator)
                if not m_task.viewing.filter(id=tmp_p.principal.id):
                    m_task.viewing.add(tmp_p.principal)
                tmp_p = tmp_p.parent

            if not m_task.viewing.filter(id=m_task.creator.id):
                m_task.viewing.add(m_task.creator)
            if not m_task.viewing.filter(id=principal.id):
                m_task.viewing.add(principal)
            m_task.save()

            Task.objects.filter(id=task_id).update(name=name, begin_date=begin_date, end_date=end_date, state=state,
                                                   content=content, finish=finish, importance=importance,
                                                   principal=principal)

            parent_obj = m_task.parent

            if parent_obj is None and parent != "None":
                if isChild(parent, m_task) is True:
                    messages.success(request, '修改失败！父任务不能是自己的子任务！')
                    return redirect("/task/modify/" + task_id + "/")
                else:
                    ppobj = Task.objects.get(id=parent)
                    m_task.move_to(ppobj, "first-child")
                    messages.success(request, '修改成功')
            elif parent_obj is not None and parent != "None":
                if parent != parent_obj.id:
                    if isChild(parent, m_task) is True:
                        messages.success(request, '修改失败！父任务不能是自己的子任务！')
                        return redirect("/task/modify/" + task_id + "/")
                    else:
                        ppobj = Task.objects.get(id=parent)
                        m_task.move_to(ppobj, "first-child")
                        messages.success(request, '修改成功')
                else:
                    messages.success(request, '修改成功')
            elif parent_obj is not None and parent == "None":
                    m_task.move_to(None, "first-child")
                    messages.success(request, '修改成功')
            else:
                messages.success(request, '修改成功')

            # cache.clear()
            #print "source:"+source
            #if source == '1':
            #return redirect("/task/created_task/")

    task = Task.objects.get(id=task_id)
    group = Group.objects.all()
    ngroup = Staff.objects.filter(group=None)
    parents = Task.objects.filter(istemp=0)
    return render_to_response('task/edit_task.html',
                              {'task': task, 'parent': parents, 'group': group, 'ngroup': ngroup,
                               'edit_task': edit_task, 'staff': request.user.staff}, context)


def isChild(id, task):
    children = task.get_children()

    for c in children:
        if c.id == id:
            return True
    return False


@login_required(login_url="/app/login/")
#@permission_required_with('task')
def psb_vsb(request, task_id):
    if task_id != "None":
        task = Task.objects.get(id=task_id)
        posible_visible = task.visible.all()
    else:
        posible_visible = Staff.objects.filter(visible=True)

    rlst = Template("{% for p in posible_visible %} <option value='{{p.id}}'>{{p}}</option>{% endfor %}")
    html = rlst.render(Context({'posible_visible': posible_visible}))
    return HttpResponse(html)


@login_required(login_url="/app/login/")
def psb_vsb_add(request, task_id, group_id):
    if task_id != 'None':
        task = Task.objects.get(id=task_id)
        posible_visible = task.viewing.all()
    else:
        posible_visible = Staff.objects.filter(visible=True)

    if group_id != 'None':
        group = Group.objects.get(id=group_id)
        gm = []
        for p in posible_visible:
            for g in group.member.all():
                if p.id == g.id:
                    gm.append(p)
        rlst = Template(
            "{% for p in posible_visible %}<option value='{{p}}' \
            {%for g in gm%}{%ifequal g.id p.id%}select='true'{% endifequal %}{%endfor%}\
            >{{p}}</option>{% endfor %}")
        html = rlst.render(Context({'posible_visible': posible_visible, 'gm': gm}))
    else:
        rlst = Template("{% for p in posible_visible %} <option value='{{p.id}}'>{{p}}</option>{% endfor %}")
        html = rlst.render(Context({'posible_visible': posible_visible}))

    return HttpResponse(html)


@login_required(login_url="/app/login/")
def add_comment(request, task_id, c_type, doc):
    context = RequestContext(request)
    if request.method == 'POST':
        nf = CommentForm(request.POST)
        if nf.is_valid():
            nf_comment = nf.save(commit=False)
            nf_comment.task = Task.objects.get(id=task_id)
            nf_comment.author = request.user
            nf_comment.date = datetime.now()
            nf_comment.type = c_type
            nf_comment.save()
            # cache.clear()
            # messages.success(request, '提交成功')
            return HttpResponse('提交成功')
        else:
            return HttpResponse('提交失败,内容不能为空')
            # messages.error(request, '提交失败,内容不能为空')

    if doc == '5':
        tasks = request.user.staff.viewing.all()
        comment = Comment.objects.all()
        nf = CommentForm()
        #cache.clear()
        return render_to_response('task/all_task.html',
                                  {'tasks': tasks, 'comments': comment, 'nf': nf, 'staff': request.user.staff},
                                  context)
    if doc == '4':
        tasks = request.user.staff.task.all()
        comment = Comment.objects.all()
        nf = CommentForm()
        #cache.clear()
        return render_to_response('task/executed_task.html', {'tasks': tasks, 'comments': comment, 'nf': nf,
                                                              'staff': request.user.staff}, context)

    if doc == '3':
        # task = Task.objects.get(id=task_id)
        # comment = Comment.objects.all()
        # #nf = CommentForm()
        # calendar = request.user.staff.visibleCalendar.all()
        # return render_to_response('task/task_details.html',
        #                   {'task': task, 'comments': comment, 'nf': nf, 'staff': request.user.staff,
        #                    'calendar': calendar}, context)
        pageURL = '/'
        if (request.POST.getlist('pageURL')):
            pageURL = request.POST.getlist('pageURL')[0]
        # print pageURL
        return HttpResponseRedirect(pageURL)
        # return render_to_response('task/task_details.html',
        #                           {'task': task, 'comments': comment, 'nf': nf, 'staff': request.user.staff,
        #                            'calendar': calendar}, context)
    if doc == '2':
        tasks = Task.objects.filter(Q(principal=request.user.staff) & Q(istemp=0))
        comment = Comment.objects.all()
        nf = CommentForm()
        #cache.clear()
        return render_to_response('task/doing_task.html',
                                  {'tasks': tasks, 'comments': comment, 'nf': nf, 'staff': request.user.staff},
                                  context)
    elif doc == '1':
        tasks = Task.objects.filter(Q(creator=request.user.staff) & Q(istemp=0))
        comment = Comment.objects.all()
        nf = CommentForm()
        #cache.clear()
        return render_to_response('task/created_task.html',
                                  {'tasks': tasks, 'comments': comment, 'nf': nf, 'staff': request.user.staff}, context)
    else:
        return render_to_response('error.html', context)


@login_required(login_url="/app/login/")
def add_schedule(request, task_id, doc):
    context = RequestContext(request)
    staff_id = request.user.staff.id
    updateSummary(int(staff_id), int(task_id))
    # cache.clear()
    messages.success(request, '加入日程成功')
    if doc == '1':
        tasks = Task.objects.filter(Q(creator=request.user.staff) & Q(istemp=0))
        comment = Comment.objects.all()
        nf = CommentForm()
        return render_to_response('task/created_task.html',
                                  {'tasks': tasks, 'comments': comment, 'nf': nf, 'staff': request.user.staff}, context)
    elif doc == '2':
        tasks = Task.objects.filter(Q(principal=request.user.staff) & Q(istemp=0))
        comment = Comment.objects.all()
        nf = CommentForm()
        return render_to_response('task/doing_task.html', {'tasks': tasks, 'comments': comment, 'nf': nf,
                                                           'staff': request.user.staff}, context)
    else:
        tasks = request.user.staff.task.all()
        comment = Comment.objects.all()
        nf = CommentForm()
        return render_to_response('task/executed_task.html', {'tasks': tasks, 'comments': comment, 'nf': nf,
                                                              'staff': request.user.staff}, context)


def settemppop(task, name, bdate, edate, content, importance):
    if name != '':
        task.name = name
    if bdate != '':
        task.begin_date = bdate
    if edate != '':
        task.end_date = edate
    if content != '':
        task.content = content
    if importance != -1:
        task.importance = importance
    task.istemp = 1

    return task


@login_required(login_url="/app/login/")
def createTreeBy(request, task_id, name, bdate, edate, content, importance, layer):
    task = Task.objects.get(id=task_id)
    root = task.clone()
    root.inername = task.id
    root.creator = request.user.staff
    root = settemppop(root, name, bdate, edate, content, importance)
    root.save()
    # cache.clear()

    tps = [task]
    ps = [root]

    ly = 1
    while True:
        if ly >= layer:
            break
        ly = ly + 1

        tps_t = []
        ps_t = []
        for i, tp in enumerate(tps):
            child = tp.get_children()
            for c in child:
                c_t = c.clone()
                c_t.creator = request.user.staff
                c_t = settemppop(c_t, name, bdate, edate, content, importance)
                c_t.inername = c.id
                c_t.parent = ps[i]
                c_t.save()
                tps_t.append(c)
                ps_t.append(c_t)

        lgth = len(tps_t)
        if lgth < 1:
            break
        else:
            tps = tps_t
            ps = ps_t

    temp = Task.objects.exclude(inername=None)

    for t in temp:
        t.inername = None
        t.save()


def create_tsktemp(request, task_id):
    context = RequestContext(request)
    if request.method == 'POST':
        name = ''
        begin_date = ''
        end_date = ''
        importance = -1
        content = ''
        task_dict = dict(request.POST.iterlists())
        if task_dict.get("name"):
            name = task_dict['name'][0].strip()
        if task_dict.get("begin_date"):
            begin_date = task_dict['begin_date'][0].strip()
        if task_dict.get("end_date"):
            end_date = task_dict['end_date'][0].strip()
        if task_dict.get("importance"):
            importance = task_dict['importance'][0].strip()
        if task_dict.get("content"):
            content = task_dict['content'][0].strip()
        layer = 999
        if task_dict.get("layer"):
            layer = task_dict['layer'][0].strip()
            if layer == '':
                layer = 999
        if name == '':
            messages.error(request, '名称不能为空！')
        elif re.search(r'/|\\|:|\*|<|>|\?|:|\"|\|', name):
            messages.error(request, '名称不能包含下列任何字符“ \ / : * ? " < > | ”')
        elif begin_date == '' or end_date == '':
            messages.error(request, '开始日期和结束日期不能为空！')
        elif content == '':
            messages.error(request, '任务内容不能为空！')
        elif not valid_time(begin_date):
            messages.error(request, '开始日期格式错误！')
        elif not valid_time(end_date):
            messages.error(request, '结束日期格式错误！')
        else:
            createTreeBy(request, task_id, name, begin_date, end_date, content, importance, int(layer))
            # cache.clear()
            messages.success(request, '模板创建成功!')
    tasks = Task.objects.filter(istemp=0)
    edit_task = request.user.staff.role.editTask
    usr = request.user
    map_task = {}
    for t in tasks:
        map_task[t.id] = 2
        for v in t.viewing.all():
            if v.id == usr.staff.id:
                map_task[t.id] = 1
                break
    return render_to_response('task/task.html', {'tasks': tasks, 'staff': request.user.staff, 'map_task': map_task,
                                                 'edit_task': edit_task}, context)


@login_required(login_url="/app/login/")
#@permission_required_with('task')
# @cache_on_auth(60 * 5)
def taskTemplate(request):
    temps = Task.objects.filter(Q(istemp=1) & Q(creator=request.user.staff))
    return render_to_response('task/taskTemplate.html', {'temps': temps, 'staff': request.user.staff})


def addByTemp(request, temp_id):
    # cache.clear()
    context = RequestContext(request)
    edit_task = request.user.staff.role.editTask

    temp = Task.objects.get(id=temp_id)
    name = temp.name
    begin_date = temp.begin_date
    end_date = temp.end_date
    state = temp.state
    importance = temp.importance
    content = temp.content
    finish = temp.finish
    principal = temp.principal

    p_parent = []
    task_execute = request.user.staff.task
    task_cp = Task.objects.filter(
        Q(istemp=True) & (Q(creator=request.user.staff) | Q(principal=request.user.staff)))

    for t1 in task_execute.all():
        has = False
        for p in p_parent:
            if p == t1:
                has = True
                break
        if not has:
            p_parent.append(t1)

    for t2 in task_cp:
        has = False
        for p in p_parent:
            if p == t2:
                has = True
                break
        if not has:
            p_parent.append(t2)

    parent = Task.objects.filter(istemp=0)

    for p in parent:
        has = False
        for t1 in p_parent:
            if p == t1:
                has = True
                break
        if not has:
            p.name = "没有权限的项目"
            p.id = -1

    staff = Staff.objects.filter(visible=True)
    group = Group.objects.all()
    ngroup = Staff.objects.filter(group=None)
    temps = Task.objects.filter(Q(istemp=1) & Q(parent=None))
    return render_to_response('task/add_task.html',
                              {'parent': parent, 'staff': request.user.staff, 'group': group, 'ngroup': ngroup,
                               't_name': name,
                               't_begin_date': begin_date, 't_end_data': end_date, 't_state': state,
                               't_importance': importance, 't_content': content, 't_finish': finish,
                               't_principal': principal, 'temps': temps, 'edit_task': edit_task}, context)


def createTaskBy(request, tmp_id, task_id):
    # cache.clear()
    temp = Task.objects.get(id=tmp_id)
    troot = Task.objects.get(id=task_id)

    tps = [temp]
    ps = [troot]

    while True:
        tps_t = []
        ps_t = []
        for i, tp in enumerate(tps):
            child = tp.get_children()
            for c in child:
                c_t = c.clone()
                c_t.inername = c.id
                c_t.parent = ps[i]
                c_t.creator = request.user.staff
                c_t.istemp = 0
                c_t.save()
                c_t.viewing.clear()
                c_t.viewing.add(request.user.staff)
                cc_t = Task.objects.get(inername=c.id)
                tps_t.append(c)
                ps_t.append(cc_t)
        lgth = len(tps_t)
        if lgth < 1:
            break
        else:
            tps = tps_t
            ps = ps_t

    temps = Task.objects.exclude(inername=None)
    for t in temps:
        t.inername = None
        t.save()


def selectTemp(request):
    context = RequestContext(request)
    edit_task = request.user.staff.role.editTask

    temp_dict = dict(request.POST.iterlists())
    if temp_dict.get('temp'):
        temp_id = temp_dict['temp'][0].strip()
        if temp_id != '-1':
            createTaskBy(temp_id)
            # cache.clear()
            messages.success(request, '成功按模板创建项目')
    else:
        messages.error(request, '请选择正确的项目模板')
    p_parent = []
    task_execute = request.user.staff.task
    task_cp = Task.objects.filter(
        Q(istemp=True) & (Q(creator=request.user.staff) | Q(principal=request.user.staff)))

    for t1 in task_execute.all():
        has = False
        for p in p_parent:
            if p == t1:
                has = True
                break
        if not has:
            p_parent.append(t1)

    for t2 in task_cp:
        has = False
        for p in p_parent:
            if p == t2:
                has = True
                break
        if not has:
            p_parent.append(t2)

    parent = Task.objects.filter(istemp=0)

    for p in parent:
        has = False
        for t1 in p_parent:
            if p == t1:
                has = True
                break
        if not has:
            p.name = "没有权限的项目"
            p.id = -1

    staff = Staff.objects.filter(visible=True)
    group = Group.objects.all()
    ngroup = Staff.objects.filter(group=None)
    temps = Task.objects.filter(Q(istemp=1) & Q(parent=None))
    return render_to_response('task/add_task.html',
                              {'parent': parent, 'staff': request.user.staff, 'group': group,
                               'edit_task': edit_task, 'ngroup': ngroup, 'temps': temps}, context)


def selTemp_addTsk(request, temp_id):
    # cache.clear()
    context = RequestContext(request)
    edit_task = request.user.staff.role.editTask
    staff = Staff.objects.filter(visible=True)
    group = Group.objects.all()
    ngroup = Staff.objects.filter(group=None)
    temps = Task.objects.filter(Q(istemp=1) & Q(parent=None))
    selTempList = Task.objects.filter(id=temp_id)
    if (selTempList.count() == 0):
        return HttpResponseRedirect('/task/add_task')
    else:
        selTemp = selTempList[0]
        name = selTemp.name
        begin_date = selTemp.begin_date
        end_date = selTemp.end_date
        state = selTemp.state
        importance = selTemp.importance
        content = selTemp.content
        finish = selTemp.finish
        principal = selTemp.principal
    parent = []
    return render_to_response('task/add_task.html',
                              {'parent': parent, 'staff': request.user.staff, 'group': group, 't_name': name,
                               't_begin_date': begin_date, 't_end_data': end_date, 't_state': state,
                               't_importance': importance, 't_content': content, 't_finish': finish,
                               'selTemp': selTemp,
                               't_principal': principal, 'edit_task': edit_task, 'ngroup': ngroup, 'temps': temps},
                              context)


def delTemp(request, temp_id):
    context = RequestContext(request)
    temp = Task.objects.get(id=temp_id)

    while temp.parent is not None:
        temp = temp.parent
    temp.delete()

    temps = Task.objects.filter(Q(istemp=1) & Q(creator=request.user.staff))
    # cache.clear()
    messages.success(request, "删除模板成功!")
    return render_to_response('task/taskTemplate.html', {'temps': temps, 'staff': request.user.staff}, context)
