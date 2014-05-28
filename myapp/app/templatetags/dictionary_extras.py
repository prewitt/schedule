#-*- coding: UTF-8 -*-
__author__ = 'Maple'
from django import template
from filebrowser.sites import site
import re
register = template.Library()


@register.filter(name='dict_access')
def dict_access(value, arg):
    return value[arg]


@register.filter(name='bigger_than')
def bigger_than(a, b):
    return a > b


@register.filter(name='n_range')
def n_range(end, start=0):
    return range(start, int(end))


@register.filter(name='staff_in')
def staff_in(staff, stf):
    if len(staff) < 1:
        return False
    for st in staff:
        if st == stf:
            return True
    return False


@register.filter(name='sub_str')
def sub_str(string, n):
    if string == '' or string == 'None' or string is None:
        return ''
    if len(string) > n:
        return string[0:n - 1] + ' ...'
    else:
        return string


@register.simple_tag(name='task_path')
def task_path(path):
    strinfo = re.compile("\\|:|\*|<|>|\?|:|\"|\|")
    path=strinfo.sub('_',path)
    site.task_path=path
    site.directory=site.srcDirectory+site.task_path
    pathList=site.directory.split('/')
    i=0
    str=''
    for item in pathList:
        if item !='':
            str+=item+'/'
            site.createTaskDir(str)
            site.task_name=item
        i+=1
