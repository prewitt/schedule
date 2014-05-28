#-*- coding: UTF-8 -*-
# Create your views here.
from  app.models import Notice, Staff
from  django.template import RequestContext
from  django.shortcuts import  render_to_response,render,get_object_or_404,redirect
from  django.http import HttpResponse, HttpResponseRedirect
from  django.contrib.auth import authenticate,login,logout
from django import  forms
from  django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from  app.views import permission_required_with, cache_on_auth
from  datetime import  datetime
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.db import router, transaction


class NoticeForm(forms.ModelForm):
    title = forms.CharField()
    time = forms.DateTimeField()
    content = forms.Textarea()

    class Meta:
        model = Notice
        exclude = ('creator',)
@login_required(login_url="/app/login/")
#@permission_required_with('notice')
def index(request):
    cache.clear()
    context = RequestContext(request)
    notices = Notice.objects.all()
    return  render_to_response('notice/index.html',{'staff': request.user.staff,'notices':notices},context)

@login_required(login_url="/app/login/")
#@permission_required_with('notice')
# @cache_on_auth(60*5)
def get_notice(request):
    context = RequestContext(request)
    notices = Notice.objects.all().order_by('-time')

    return  render_to_response('notice/notice_list.html',{'notice_list':notices,'url':request.path,'staff':request.user.staff},context)

@login_required(login_url="/app/login/")
#@permission_required_with('notice')
def detail_notice(request,id):
    context = RequestContext(request)
    notice = Notice.objects.get(id=id)
    enablecalendar = request.user.staff.role.editCalendar
    calendar = request.user.staff.visibleCalendar.all()
    return render_to_response('notice/detail_notice.html',{'calendar': calendar, 'enCalendar': enablecalendar,'staff': request.user.staff,'notice':notice},context)


@login_required(login_url='/app/login/')
def delete_notice(request, id):
    context = RequestContext(request)
    Notice.objects.get(id=id).delete()
    cache.clear()
    messages.success(request,"删除成功！")
    notices = Notice.objects.all().order_by('-time')
    return  render_to_response('notice/notice_list.html',{'notice_list':notices,'url':request.path,'staff':request.user.staff},context)


@login_required(login_url="/app/login/")
#@permission_required_with('notice')
def create_notice(request):
    context = RequestContext(request)
    if request.method == 'POST':
        nf = NoticeForm(request.POST)
        if nf.is_valid():
            nf_comment=nf.save(commit=False)
            nf_comment.creator = request.user.staff
            nf_comment.save()
            cache.clear()

            messages.success(request,"创建通知成功!")
            return redirect("/notice/get_notice/")
        else:
            title = request.POST.get('title')
            content = request.POST.get('content')
            time = request.POST.get('time')
            if title == '':
                messages.error(request,"请填写标题！")
            elif time == '':
                messages.error(request,'请选择时间！')
            elif content == '':
                messages.error(request,'请填写内容！')
            elif time != '':
                messages.error(request,'时间格式不正确！')
            elif len(title) > 30:
                messages.error(request,'标题太长（应不大于30个字）！')

            return render_to_response('notice/create_notice.html',
                                      {'staff': request.user.staff,'title':title,'content':content,'time':time},
                                      context)
    return render_to_response('notice/create_notice.html',{'staff': request.user.staff},context)
