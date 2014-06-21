#-*- coding: UTF-8 -*-
from django.db import models
from  django.contrib.auth.models import User
# Create your models here.
from mptt.models import MPTTModel, TreeForeignKey


class Role(models.Model):
    name = models.CharField(max_length=20)
    level = models.PositiveSmallIntegerField(default=5)  #the smaller the power
    editStaff = models.BooleanField(default=True)
    editTask = models.BooleanField(default=True)
    editCalendar = models.BooleanField(default=True)
    editMeeting = models.BooleanField(default=True)
    exportFile = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class Staff(models.Model):
    user = models.OneToOneField(User, unique=True, related_name='staff')
    name = models.CharField(max_length=20)
    gender = models.BooleanField(default=True)  #True:man
    visible = models.BooleanField(default=True)
    role = models.ForeignKey(Role, related_name='staff')
    content = models.CharField(max_length=1024)
    visibleStaff = models.ManyToManyField("self", verbose_name='可见度', symmetrical=False, related_name='visibleCalendar',
                                          null=True)

    def __unicode__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=20)
    member = models.ManyToManyField(Staff, related_name='group', blank=True, null=True)
    leader = models.ForeignKey(Staff, related_name='leader', blank=True, null=True)
    content = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.name


class Task(MPTTModel):
    name = models.CharField(max_length=20, verbose_name='名称')
    creator = models.ForeignKey(Staff, related_name='created', verbose_name='创建者')
    create_date = models.DateTimeField()
    begin_date = models.DateTimeField(verbose_name='开始日期')
    end_date = models.DateTimeField(verbose_name='结束日期')
    state = models.IntegerField(verbose_name='状态')
    importance = models.IntegerField(verbose_name='等级')
    content = models.TextField(verbose_name='内容', max_length=1024)
    finish = models.TextField(max_length=1024, verbose_name='完成标志', blank=True, null=True)
    parent = TreeForeignKey('self', verbose_name='父任务', related_name='child', blank=True, null=True)
    principal = models.ForeignKey(Staff, verbose_name='负责人', related_name='directed')
    executor = models.ManyToManyField(Staff, verbose_name='执行人', related_name='task', null=True)
    group = models.ManyToManyField(Group, verbose_name='所属组', related_name='group', blank=True, null=True)
    viewing = models.ManyToManyField(Staff, verbose_name='可见性', related_name='viewing', null=True)
    inername = models.IntegerField(verbose_name='名称', blank=True, null=True)
    istemp = models.IntegerField(verbose_name='是否模板', default=0)

    class MPTTMeta:
        level_attr = 'mptt_level'
        order_insertion_by = ['-begin_date']

    def __unicode__(self):
        return self.name

    def clone(self):
        tsk = Task()
        tsk.name = self.name
        tsk.creator = self.creator
        tsk.create_date = self.create_date
        tsk.begin_date = self.begin_date
        tsk.end_date = self.end_date
        tsk.state = self.state
        tsk.importance = self.importance
        tsk.content = self.content
        tsk.finish = self.finish
        tsk.parent = self.parent
        tsk.principal = self.principal
        return tsk


class Comment(models.Model):
    author = models.ForeignKey(User)
    date = models.DateTimeField()
    content = models.TextField(max_length=1024, verbose_name='内容')
    task = models.ForeignKey(Task)
    type = models.IntegerField()

    def __unicode__(self):
        return self.author.username + ' comment:'


class Meeting(models.Model):
    name = models.CharField(max_length=30)
    time = models.DateTimeField()
    member = models.ManyToManyField(Staff, related_name='joined_meeting', blank=True, null=True)
    place = models.CharField(max_length=50)
    originator = models.ForeignKey(Staff)
    content = models.TextField()

    def __unicode__(self):
        return self.name


class Notice(models.Model):
    creator = models.ForeignKey(Staff, null=True)
    title = models.CharField(max_length=30)
    time = models.DateTimeField()
    content = models.TextField()

    def __unicode__(self):
        return self.title


class Calendar(models.Model):
    creator = models.ForeignKey(Staff)
    date = models.DateTimeField()
    summary = models.TextField(verbose_name='概括', null=True)
    content8 = models.TextField(null=True, default='')
    content9 = models.TextField(null=True, default='')
    content10 = models.TextField(null=True, default='')
    content11 = models.TextField(null=True, default='')
    content12 = models.TextField(null=True, default='')
    content13 = models.TextField(null=True, default='')
    content14 = models.TextField(null=True, default='')
    content15 = models.TextField(null=True, default='')
    content16 = models.TextField(null=True, default='')
    content17 = models.TextField(null=True, default='')
    content18 = models.TextField(null=True, default='')
    content19 = models.TextField(null=True, default='')
    content20 = models.TextField(null=True, default='')
    content21 = models.TextField(null=True, default='')
    content22 = models.TextField(null=True, default='')
    content23 = models.TextField(null=True, default='')
    #def __unicode__(self):
    #    return self.name


class Bug(models.Model):
    name = models.CharField(max_length=20, verbose_name='名称')
    creator = models.ForeignKey(Staff, related_name='b_creator', verbose_name='创建者')
    create_date = models.DateTimeField()
    begin_date = models.DateTimeField(verbose_name='开始日期')
    end_date = models.DateTimeField(verbose_name='结束日期')
    state = models.IntegerField(verbose_name='状态')
    importance = models.IntegerField(verbose_name='等级')
    content = models.TextField(verbose_name='内容', max_length=1024)
    finish = models.TextField(max_length=1024, verbose_name='完成标志', blank=True, null=True)
    task = models.ForeignKey(Task, verbose_name='所属任务', related_name='b_bug')
    principal = models.ForeignKey(Staff, verbose_name='负责人', related_name='b_principal')
    executor = models.ManyToManyField(Staff, verbose_name='执行人', related_name='b_executor', null=True)
    group = models.ManyToManyField(Group, verbose_name='所属组', related_name='b_group', blank=True, null=True)

    def __unicode__(self):
        return self.name


class BugComment(models.Model):
    author = models.ForeignKey(Staff)
    date = models.DateTimeField()
    content = models.TextField(max_length=1024, verbose_name='内容')
    bug = models.ForeignKey(Bug)
    type = models.IntegerField()

    def __unicode__(self):
        return self.author.name + " at " + self.date + " said: " + self.content + "\n"


class UnreadComment(models.Model):
    task = models.ForeignKey(Task, related_name='unread_comment')
    user = models.ForeignKey(Staff)
    counts = models.IntegerField(verbose_name='条数')
