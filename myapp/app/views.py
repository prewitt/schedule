#-*- coding: UTF-8 -*-
# Create your views here.
import sys
from django.db.models import Q

reload(sys)
sys.setdefaultencoding('utf-8')
from  django.template import RequestContext
from  django.shortcuts import render_to_response, render
from  django.http import HttpResponse, HttpResponseRedirect
from  django.contrib.auth import authenticate, login, logout
from django import forms
from models import Staff, Task
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from  django.contrib.auth.models import User, check_password, make_password
from django.contrib import messages
from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
import hashlib
from django.utils.crypto import constant_time_compare
from django.utils.datastructures import SortedDict
from functools import wraps
from django.utils.decorators import available_attrs
from django.core.cache import cache
from django.views.decorators.cache import never_cache
from  datetime import datetime, date, timedelta
from  models import Meeting
from django.views.decorators.cache import cache_page
# 检验输入时间是否合法
def valid_time(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def get_week_days(year, week):
    d = datetime(year, 1, 1, hour=23, minute=59)
    if (d.weekday() > 3):
        d = d + timedelta(7 - d.weekday())
    else:
        d = d - timedelta(d.weekday())
    dlt = timedelta(days=(week - 1) * 7)
    return d + dlt, d + dlt + timedelta(days=6)

# used for md5 ,save password
class MyPasswordHasher(BasePasswordHasher):
    algorithm = 'md5_16'

    def encode(self, password, salt=None, iterations=None):
        return "%s" % (hashlib.md5(password).hexdigest()[8:-8])

    def verify(self, password, encoded):
        encoded_2 = self.encode(password)
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        return SortedDict([
            (('hash'), mask_hash(encoded)),
        ])

# custom backend for using authenticate
class MyCustomBackend:
    # Create an authentication method
    # This is called by the standard Django login procedure
    def authenticate(self, username=None, password=None):

        try:
            # Try to find a user matching your username
            user = User.objects.get(username=username)

            #  Check the password is the reverse of the username
            if make_password(password) == user.password:
                # Yes? return the Django user object
                return user
            else:
                # No? return None - triggers default login failed
                return None
        except User.DoesNotExist:
            # No user was found, return None - triggers default login failed
            return None

    # Required for your backend to work properly - unchanged in most scenarios
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

# set a context
#def my_staff(request):
#    me_staff =request.user.staff
#    context = {'me_staff':me_staff}
#    return  context
def cache_on_auth(timeout):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            return cache_page(timeout, key_prefix="_auth_%s_" % request.user.username)(view_func)(request, *args,
                                                                                                  **kwargs)

        return _wrapped_view

    return decorator

#with parameter
def permission_required_with(parameter):
    def decorator(view_func): #second wrapper gets view_func
        @wraps(view_func, assigned=available_attrs(view_func))
        def wrapper(request, *args, **kwargs):
            if parameter == 'task':
                if not request.user.staff.role.editTask:
                    permission = '任务管理权限'
                    return render_to_response('error.html', {'permission': permission})
                return view_func(request, *args, **kwargs)
            elif parameter == 'calendar':
                if not request.user.staff.role.editCalendar:
                    permission = '日历功能权限'
                    return render_to_response('error.html', {'permission': permission})
                return view_func(request, *args, **kwargs)
            elif parameter == 'staff':
                if not request.user.staff.role.editStaff:
                    permission = '人员管理权限'
                    return render_to_response('error.html', {'permission': permission})
                return view_func(request, *args, **kwargs)
            elif parameter == 'meeting':
                if not request.user.staff.role.editMeeting:
                    permission = '会议权限'
                    return render_to_response('error.html', {'permission': permission})
                return view_func(request, *args, **kwargs)
            elif parameter == 'notice':
                if not request.user.staff.role.editMeeting:
                    permission = '通知权限'            #if item_id == parameter:
                    return render_to_response('error.html', {'permission': permission})
                return view_func(request, *args, **kwargs)
            permission = '未知参数'
            return render_to_response('error.html', {'permission': permission})

        return wrapper

    return decorator


@never_cache
def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)
    username = ''
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            messages.error(request, '用户名或密码错误!')
    return render_to_response('app/login.html', {'username': username}, context)


# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required(login_url="/app/login/")
def user_logout(request):
    cache.clear()
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/')


@login_required(login_url="/app/login/")
# @cache_on_auth(60 * 15)
def index(request):
    me = request.user.staff
    context = RequestContext(request)
    #yestday
    now = datetime.now() - timedelta(days=1)
    joined_meeting = me.joined_meeting.filter(time__gte=now).order_by('time')
    launched_meeting = me.meeting_set.filter(time__gte=now).order_by('time')

    week = now.isocalendar()[1]
    monday, weekend = get_week_days(now.year, week)
    week_meeting_joined = me.joined_meeting.filter(time__gte=now).exclude(time__gte=weekend)
    week_meeting_launched = me.meeting_set.filter(time__gte=now).exclude(time__gte=weekend)

    affirm_task = me.directed.filter(Q(state=1) & Q(istemp=0)).order_by('end_date')
    submit_task = me.directed.filter(Q(state=2) & Q(istemp=0)).order_by('end_date')
    check_task = me.created.filter(Q(state=3) & Q(istemp=0)).order_by('end_date')
    #check_task = Task.objects.all()

    #cache.clear()
    return render_to_response('app/index.html',
                              {'staff': request.user.staff,
                               'joined_meeting': joined_meeting,
                               'launched_meeting': launched_meeting,
                               'affirm_task': affirm_task,
                               'submit_task': submit_task,
                               'check_task': check_task,
                               'week_num_joined': len(week_meeting_joined),
                               'week_num_launched': len(week_meeting_launched)}, context)

def change_password(request):
    context = RequestContext(request)
    if request.method == 'POST':
        password = request.POST['password']
        newpassord1 = request.POST['newpassword1']
        newpassord2 = request.POST['newpassword2']
        if password == "":
            messages.error(request, '原密码不能为空！')
        elif newpassord1 == "":
            messages.error(request, '请输入新密码！')
        elif newpassord2 != newpassord1:
            messages.error(request, '两次输入不一致！')
        else:
            user = authenticate(username=request.user.username, password=password)
            if user is not None:
                u = request.user
                u.set_password(newpassord1)
                u.save()
                messages.success(request, '密码更改成功！')
            else:
                messages.error(request, '原密码输入不正确！')
        cache.clear()
    return render_to_response('app/change_password.html', {'staff': request.user.staff}, context)
