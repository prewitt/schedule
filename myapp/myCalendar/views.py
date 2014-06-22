#-*- coding: UTF-8 -*-
__author__ = 'PW'
import  datetime
from models import ContestCalendar
from django.shortcuts import render_to_response, RequestContext
from django.utils.safestring import mark_safe
from datetime import date
from  app.models import Calendar,Task,Staff,Bug
from  django.contrib.auth.models import User
from models import DayItem
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.views import permission_required_with
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.db.models import F
from bulk_update.helper import bulk_update
from django.db import connection,transaction

@login_required(login_url="/app/login/")
def named_month(pMonthNumber):
    """
    Return the name of the month, given the month number
    """
    return date(1900, pMonthNumber, 1).strftime('%B')


@login_required(login_url="/app/login/")
#@permission_required_with('calendar')
def home(request, pStaffID):
    """
    Show calendar of events this month
    """
    lToday = datetime.datetime.now()
    return calendar(request, lToday.year, lToday.month, pStaffID)


@login_required(login_url="/app/login/")
#@permission_required_with('calendar')
def calendar(request, pYear, pMonth, pStaffID):
    """
    Show calendar of events for specified month and year
    """
    lYear = int(pYear)
    lMonth = int(pMonth)
    lStaffID = int(pStaffID)
    if (lStaffID == 0):
        me = True
        staff = request.user.staff
    else:
        me = False
        staff=Staff.objects.get(id=lStaffID)
    lContestEvents = Calendar.objects.filter(creator=staff,date__year=lYear,date__month=lMonth)
    lCalendar = ContestCalendar(lStaffID,lContestEvents).formatmonth(lYear, lMonth)
    lPreviousYear = lYear
    lPreviousMonth = lMonth - 1
    if lPreviousMonth == 0:
        lPreviousMonth = 12
        lPreviousYear = lYear - 1
    lNextYear = lYear
    lNextMonth = lMonth + 1
    if lNextMonth == 13:
        lNextMonth = 1
        lNextYear = lYear + 1
    lYearAfterThis = lYear + 1
    lYearBeforeThis = lYear - 1

    return render_to_response( 'calendar/calendar.html', {'Calendar' : mark_safe(lCalendar),
                                                       'StaffID':lStaffID,
                                                       'Month' : lMonth,
                                                      # 'MonthName' : lMonth,
                                                       'Year' : lYear,
                                                       'PreviousMonth' : lPreviousMonth,
                                                      # 'PreviousMonthName' : lPreviousMonth,
                                                       'PreviousYear' : lPreviousYear,
                                                       'NextMonth' : lNextMonth,
                                                      # 'NextMonthName' : lNextMonth,
                                                       'NextYear' : lNextYear,
                                                       'YearBeforeThis' : lYearBeforeThis,
                                                       'YearAfterThis' : lYearAfterThis,
                                                       'staff':staff,
                                                       'me':me,
                                                   })

@login_required(login_url="/app/login/")
#@permission_required_with('calendar')
def todayItems(request):
    """
        get today items to display on html
    """
    lToday = datetime.datetime.now()
    return getDayItems(request, lToday.year, lToday.month, lToday.day, 0)

def updateSummary(staffID,taskID):
    """
        updateTheSummary
    """
    lToday = datetime.datetime.now()
    lYear = int(lToday.year)
    lMonth = int(lToday.month)
    lDay=int(lToday.day)
    staff=Staff.objects.get(id=staffID)
    mySummary=Task.objects.get(id=taskID).name.strip()
    if Calendar.objects.filter(date=datetime.datetime(lYear, lMonth, lDay, 0),creator=staff).count()==0:
        Calendar.objects.create(date=datetime.datetime(lYear, lMonth, lDay, 0), summary=mySummary, creator=staff)
    else:
        calendar=Calendar.objects.get(date=datetime.datetime(lYear, lMonth, lDay, 0), creator=staff)
        calendar.summary=mySummary
        calendar.save()

def appendSummaryPeriod(staffID,taskID):
    staff=Staff.objects.get(id=staffID)
    task=Task.objects.get(id=taskID)
    appendSummaryPeriodDetail(staff,task)

def appendSummaryBugPeriod(staffID,bugID):
    staff=Staff.objects.get(id=staffID)
    bug=Bug.objects.get(id=bugID)
    appendSummaryPeriodDetail(staff,bug)

def appendSummaryPeriodDetail(staff,task_or_bug):
    """
        appendTheSummary
    """
    # staff=Staff.objects.get(id=staffID)
    # task=Task.objects.get(id=taskID)
    mySummary=task_or_bug.name.strip()
    start=task_or_bug.begin_date
    end=task_or_bug.end_date
    calendars=Calendar.objects.filter(date__range=[start,end],creator=staff).order_by('date').all()
    for c in calendars:
        if(c.summary):
            c.summary+="; "+mySummary
        else:
            c.summary=mySummary
    if calendars and len(calendars)>0:
        bulk_update(calendars,update_fields=['summary'],batch_size=400)
    transaction.commit_unless_managed()
    index=0
    length=len(calendars)
    new_calendar=[]
    for n in range(int ((end - start).days)+1):
        date=start + datetime.timedelta(n)
        lYear = int(date.year)
        lMonth = int(date.month)
        lDay=int(date.day)
        if(index<length and date==calendars[index].date):
            index=index+1
        else:
            tmp_cal=Calendar()
            tmp_cal.date=datetime.datetime(lYear, lMonth, lDay, 0)
            tmp_cal.summary=mySummary
            tmp_cal.creator=staff
            new_calendar.append(tmp_cal)
    if new_calendar and len(new_calendar)>0:
        Calendar.objects.bulk_create(new_calendar)
    del new_calendar


def updateSummaryBug(staffID,bugID):
    """
        updateTheSummary
    """
    lToday = datetime.datetime.now()
    lYear = int(lToday.year)
    lMonth = int(lToday.month)
    lDay=int(lToday.day)
    staff=Staff.objects.get(id=staffID)
    mySummary=Bug.objects.get(id=bugID).name.strip()
    if Calendar.objects.filter(date=datetime.datetime(lYear, lMonth, lDay, 0),creator=staff).count()==0:
        Calendar.objects.create(date=datetime.datetime(lYear, lMonth, lDay, 0), summary=mySummary, creator=staff)
    else:
        calendar=Calendar.objects.get(date=datetime.datetime(lYear, lMonth, lDay, 0), creator=staff)
        calendar.summary=mySummary
        calendar.save()

@login_required(login_url="/app/login/")
#@permission_required_with('calendar')
def getDayItems(request, pYear, pMonth, pDay, pStaffID):
    """
        get day items to display on html
    """
    context = RequestContext(request)
    addDayItems(request, pYear, pMonth, pDay)
    result,response=changeTable(request, pYear, pMonth, pDay)
    lYear = int(pYear)
    lMonth = int(pMonth)
    lDay=int(pDay)
    lStaffID=int(pStaffID)
    if(lStaffID==0):
        me = True
        staff=request.user.staff
    else:
        me = False
        staff=Staff.objects.get(id=lStaffID)
    lContestEvents = Calendar.objects.filter(date__year=lYear,date__month=lMonth,date__day=pDay,creator=staff)
    if lContestEvents.count()!=0:
        dayModel=DayItem(lStaffID,lContestEvents[0])
    else:
        dayModel=DayItem(lStaffID,None)
    myDaySummary=dayModel.getDaySummary()
    if(not result):
        myDayItem=dayModel.formatItems()
    else:
        myDayItem=response
        myDict = dict(request.POST.iterlists())
        myDaySummary=myDict['summary'][0]
    myUrl='/calendar/%s/%s/' %(pYear,pMonth)
    nowUrl='/calendar/%s/%s/%s/%s/' %(pYear,pMonth,pDay,pStaffID)
    return render_to_response( 'calendar/dayItems.html', {'DayItems' : mark_safe(myDayItem),
                                                       'DaySummary':mark_safe(myDaySummary),
                                                       'OldUrl':mark_safe(myUrl),
                                                       'nowUrl':mark_safe(nowUrl),
                                                       'me':me,
                                                       'year':pYear,
                                                       'month':pMonth,
                                                       'day':pDay},context)

@login_required(login_url="/app/login/")
#@permission_required_with('calendar')
def changeTable(request, pYear, pMonth, pDay):
    """
        change the table
    """
    if request.method == "POST":
        myDict = dict(request.POST.iterlists())
        if(not myDict.get('addTd') and not myDict.get('minsTd')):
            return False,''
        if(myDict.get('addTd')):
            i=int(myDict['addTd'][0])
            myDayItem=myDict['content']
            myDayItem[i]+=myDayItem[i+1]
            del myDayItem[i+1]
            myDayItemNum=myDict['contentNum']
            myDayItemNum[i]=int(myDayItemNum[i+1])+int(myDayItemNum[i])
            del myDayItemNum[i+1]
        elif(myDict.get('minsTd')):
            i=int(myDict['minsTd'][0])
            myDayItem=myDict['content']
            myDayItem.insert(i+1,"")
            myDayItemNum=myDict['contentNum']
            myDayItemNum.insert(i+1,1)
            myDayItemNum[i]=int(myDayItemNum[i])-1
        body=''
        num=0

        for i in range(0,len(myDayItem)):
            body+=('<tr class="control-group">')
            body+=('<td rowspan="%d" class="control-label" id="dayItemTime">' %(int(myDayItemNum[i])))
            body+=('<input type="text" name="contentNum" style="display:none"  value="%d">' %(int(myDayItemNum[i])))#input means the number of this td
            body+=('%02d:00 - %02d:00</td>' %(8+num,8+num+int(myDayItemNum[i])))

            body+=('<td rowspan="%d" class="controls" id="dayItemContent">' %(int(myDayItemNum[i])))
            body+=('<textarea id="dayItemText" rows="%d" name="content">' %(int(myDayItemNum[i])))
            body+=myDayItem[i]
            body+=('</textarea>')
            if(i<len(myDayItem)-1):
                body+=('<button submit="button" name="addTd"  value="%d" class="btn btn-mini btn-primary dayitems_button" >+</button>' %(i))
            if(int(myDayItemNum[i])>1):
                body+=('<button submit="button" name="minsTd" value="%d" class="btn btn-mini btn-primary dayitems_button" >-</button>' %(i))
            body+=('</td>')
            body+=('</tr>')
            for j in range(0,int(myDayItemNum[i])-1):
                body+=('<tr class="control-group"></tr>')
            num+=int(myDayItemNum[i])
        return True,body
    return False,''





@login_required(login_url="/app/login/")
#@permission_required_with('calendar')
def addDayItems(request, pYear, pMonth, pDay):
    """
        add day items to db
    """
    lYear = int(pYear)
    lMonth = int(pMonth)
    lDay = int(pDay)
    if request.method == "POST":
        myDict = dict(request.POST.iterlists())
        if(not myDict.get('saveTable')):
            return
        myList = myDict['content']
        myListNum = myDict['contentNum']
        mySummary = myDict['summary'][0].strip()
        Calendar.objects.filter(date=datetime.datetime(lYear, lMonth, lDay, 0), creator=request.user.staff).delete()
        i = 0
        notNullNum=0
        myContent=[]
        for item in myList:
            for j in range(0,int(myListNum[i])):
                myContent.append(item)
            i = i + 1
            if item!='':
                notNullNum+=1
        if(mySummary == '' and notNullNum ==0):
            return
        calendar=Calendar.objects.create(date=datetime.datetime(lYear, lMonth, lDay, 0),creator=request.user.staff)
        calendar.content8= myContent[0]
        calendar.content9= myContent[1]
        calendar.content10=myContent[2]
        calendar.content11=myContent[3]
        calendar.content12=myContent[4]
        calendar.content13=myContent[5]
        calendar.content14=myContent[6]
        calendar.content15=myContent[7]
        calendar.content16=myContent[8]
        calendar.content17=myContent[9]
        calendar.content18=myContent[10]
        calendar.content19=myContent[11]
        calendar.content20=myContent[12]
        calendar.content21=myContent[13]
        calendar.content22=myContent[14]
        calendar.content23=myContent[15]
        if(mySummary == '' and notNullNum !=0):
            mySummary = '无概括'
        calendar.summary=mySummary
        calendar.save()
        cache.clear()
        messages.success(request, "更新成功！")
    return


@login_required(login_url="/app/login/")
#@permission_required_with('calendar')
def showList(request):
    """
        show others` calendar
    """
    lToday = datetime.datetime.now()
    lYear = int(lToday.year)
    lMonth = int(lToday.month)
    lDay=int(lToday.day)
    StaffDict={}
    if request.user.staff.role.editCalendar==False:
        staffList=request.user.staff.visibleCalendar.all().filter(visible=True)
    else:
        staffList=Staff.objects.filter(visible=True)
    for staff in staffList:
        list=Calendar.objects.filter(date=datetime.datetime(lYear, lMonth, lDay, 0),creator=staff)
        if(list.count()==1):
            StaffDict[staff]=list[0].summary
        else:
            StaffDict[staff]=''
    return render_to_response( 'calendar/list.html', {'StaffList' : StaffDict,'staff':request.user.staff})


