#-*- coding: UTF-8 -*-
# Create your views here.
from app.models import Meeting, Staff
from django.template import RequestContext
from django.shortcuts import render_to_response, render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.contrib.auth.models import User
import socket
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.views import permission_required_with,valid_time, cache_on_auth
import  datetime
from app.models import Group
from django.core.cache import cache
from django.views.decorators.cache import cache_page

class MeetingForm(forms.ModelForm):
    name = forms.CharField()
    time = forms.DateTimeField()
    place = forms.CharField()
    content = forms.Textarea()
    class Meta:
        model = Meeting
        exclude = ('originator',)


@login_required(login_url="/app/login/")
#@permission_required_with('meeting')
# @cache_on_auth(60 * 15)
def get_meeting(request):
    context = RequestContext(request)
    meetings = Meeting.objects.all()
    return render_to_response('meeting/meeting_list.html', {'meeting_list': meetings, 'url': request.path,'staff':request.user.staff}, context)

@login_required(login_url="/app/login/")
def delete_meeting(request, id):
    context = RequestContext(request)
    Meeting.objects.get(id=id).delete()
    cache.clear()
    messages.success(request, '删除成功！')
    meetings = Meeting.objects.all()
    return render_to_response('meeting/meeting_list.html', {'meeting_list': meetings, 'url': request.path,'staff':request.user.staff}, context)

@login_required(login_url="/app/login/")
#@permission_required_with('meeting')
def detail_meeting(request, id):
    context = RequestContext(request)
    meeting = Meeting.objects.get(id=id)
    enablecalendar = request.user.staff.role.editCalendar
    calendar = request.user.staff.visibleCalendar.all()
    return render_to_response('meeting/detail_meeting.html', {'calendar': calendar, 'enCalendar': enablecalendar,'staff': request.user.staff,'meeting': meeting}, context)


@login_required(login_url="/app/login/")
#@permission_required_with('meeting')
def create_meeting(request):
    context = RequestContext(request)
    group = Group.objects.all()
    ngroup = Staff.objects.filter(group=None)
    if request.method == 'POST':
        name = request.POST.get('name')
        time = request.POST.get('time')
        place = request.POST.get('place')
        content = request.POST.get('content')
        my_dict = dict(request.POST.iterlists())
        member = []
        if my_dict.get('member'):
            for m in my_dict['member']:
                member.append(Staff.objects.get(id=m))
        if name == '':
            messages.error(request, "请填写标题！")
        elif time == '':
            messages.error(request, "请选择时间！")
        elif place == '':
            messages.error(request, "请填写地点！")
        elif content == '':
            messages.error(request, "请填写内容！")
        elif len(name) > 30:
            messages.error(request,"名称太长（应不大于30个字）！")
        elif not valid_time(time):
            messages.error(request, "时间格式不正确！")
        elif len(place) > 50:
            messages.error(request,'地点太长（应不大于50字）！')
        else:
            meeting = Meeting()
            meeting.name = name
            meeting.time = time
            meeting.place = place
            meeting.originator = request.user.staff
            meeting.content = content
            meeting.save()
            for m in member:
                meeting.member.add(m)

            messages.success(request,'创建会议成功！')
            return  redirect("/meeting/get_meeting/")
            cache.clear()
        return render_to_response('meeting/create_meeting.html',
                                      {'staff': request.user.staff,'name': name, 'time': time, 'place': place,
                                       'content': content,'group':group,'ngroup':ngroup,'member':member},
                                      context)
    return render_to_response('meeting/create_meeting.html',{'staff': request.user.staff,'group':group,'ngroup':ngroup,}, context)