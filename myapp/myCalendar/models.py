#-*- coding: UTF-8 -*-
__author__ = 'PW'
from django.utils.html import conditional_escape as esc
from django.utils.safestring import mark_safe
from itertools import groupby
from calendar import HTMLCalendar, monthrange
from datetime import date
from  app.models import Calendar

class ContestCalendar(HTMLCalendar):
    Chinese_day = [u"一", u"二", u"三", u"四", u"五", u"六", u"日"]
    def __init__(self, id,pContestEvents):
        super(ContestCalendar, self).__init__()
        self.contest_events = self.group_by_day(pContestEvents)
        self.id=id

    def formatday(self, day, weekday):#override
        if day != 0:
            cssclass = self.cssclasses[weekday]
            cssclass += ' get_day_items'
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
            if day in self.contest_events:
                cssclass += ' filled'
                body = []
                #body.append('<div id="daySummary"><a   href="/calendar/%s/%s/%s">' % (self.year,self.month,day))
                body.append('<div class="get_day_items_div" year="%s" month="%s" day="%s" id="%s" href="#">' % (self.year,self.month,day,self.id))
                body.append(esc(self.contest_events[day]))
                body.append('</div>')
                return self.day_cell(cssclass, '<div class="dayNumber">%d</div> %s' % (day, ''.join(body)))
            else:
                body = []
                #body.append('<div id="daySummary"><a  href="/calendar/%s/%s/%s">' % (self.year,self.month,day))
                body.append('<div class="get_day_items_div" year="%s" month="%s" day="%s" id="%s" href="#">' % (self.year,self.month,day,self.id))
                body.append(u'')
                body.append('</div>')
                return self.day_cell(cssclass, '<div class="dayNumber">%d</div> %s' % (day, ''.join(body)))
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month):#override
        self.year, self.month = year, month
        return super(ContestCalendar, self).formatmonth(year, month)

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        if withyear:
            s = u'%s年%s月' % (theyear,themonth )
        else:
            s = u'%s月' % themonth
        return '<tr><th colspan="7" class="month"><h4>%s</h4></th></tr>' % s

    def formatweekday(self, day):
        """
        Return a weekday name as a table header.
        """
        return '<th class="%s">%s</th>' % (self.cssclasses[day], self.Chinese_day[day])

    def group_by_day(self, pContestEvents):
        #field = lambda contest: contest.date_of_event.day
        #field = lambda contest: contest.content
        tmpDict={}
        for tmp in pContestEvents:
            tmpDict[tmp.date.day]=tmp.summary
        return tmpDict
        #return dict(
        #    [(day, list(items)) for day, items in groupby(pContestEvents, field)]
        #    for tmp in pContestEvents
        #)

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)

class DayItem():
#    #def getDaySummary(self,itemEvents):
#    #    if(len(itemEvents))
    def __init__(self, id,itemEvents):
        self.getDayItems(itemEvents)
        self.id=id

    def getDayItems(self,itemEvents):
        self.dayItems={}
        for i in range(0,24):
            self.dayItems[i]=''
        self.daySummary=''
        if itemEvents!=None:
            self.dayItems[8] =itemEvents.content8
            self.dayItems[9] =itemEvents.content9
            self.dayItems[10]=itemEvents.content10
            self.dayItems[11]=itemEvents.content11
            self.dayItems[12]=itemEvents.content12
            self.dayItems[13]=itemEvents.content13
            self.dayItems[14]=itemEvents.content14
            self.dayItems[15]=itemEvents.content15
            self.dayItems[16]=itemEvents.content16
            self.dayItems[17]=itemEvents.content17
            self.dayItems[18]=itemEvents.content18
            self.dayItems[19]=itemEvents.content19
            self.dayItems[20]=itemEvents.content20
            self.dayItems[21]=itemEvents.content21
            self.dayItems[22]=itemEvents.content22
            self.dayItems[23]=itemEvents.content23
            self.daySummary=itemEvents.summary
        return self.dayItems
    def getDaySummary(self):
        return self.daySummary
    def formatItems(self):
        body=''
        items={}
        for i in range(0,24):
            items[i]=1
        k=8
        for i in range(8,23):
            if(self.dayItems[i]!="" and self.dayItems[i+1]==self.dayItems[i]):
                items[k]+=1
                items[i+1]=0
            else:
                k=i+1
        num=0
        for i in range(0,24)[::-1]:
            if(items[i]!=0):
                num=i
                break
        k=0
        for i in self.dayItems:
            if(i>=8):
                body+=('<tr class="control-group">')
                if(items[i]>0):
                    body+=('<td rowspan="%d" class="control-label" id="dayItemTime" >' %(items[i]))
                    body+=('<input type="text" name="contentNum" style="display:none"  value="%d">' %(items[i]))
                    body+=('%02d:00 - %02d:00</td>' %(i,i+items[i]))

                    body+=('<td rowspan="%d" class="controls" id="dayItemContent" >' %(items[i]))
                    body+=('<textarea id="dayItemText" rows="%d" name="content"' %(items[i]))
                    if(self.id!=0):
                        body+=('readonly=true')
                    body+=('>')
                    body+=self.dayItems[i]
                    body+=('</textarea>')
                    if(self.id==0):
                        if(i<num):
                            body+=('<button submit="button" name="addTd"  value="%d" class="btn btn-mini btn-primary dayitems_button" >+</button>' %(k))
                        if(items[i]>1):
                            body+=('<button submit="button" name="minsTd" value="%d" class="btn btn-mini btn-primary dayitems_button" >-</button>' %(k))
                    body+=('</td>')
                    k+=1
                body+=('</tr>')
        return body




