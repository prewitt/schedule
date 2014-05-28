#-*- coding: UTF-8 -*-
__author__ = 'PW'

from django.shortcuts import render_to_response,HttpResponse
from app.models import Staff,Role,Group,Calendar
from  django.contrib.auth.models import User,make_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from  django.template import RequestContext
import  hashlib
from app.views import permission_required_with
from django.core.cache import cache
from django.core.cache import cache
from django.views.decorators.cache import cache_page
@login_required(login_url="/app/login/")
@permission_required_with('staff')
def create(request):
    """
    show the add_staff html
    """
    context = RequestContext(request)
    result,response=createStaff(request)
    if(not result):
        lContestEvents = Role.objects.exclude(name="admin").order_by('name')
        lContestEventsGroup = Group.objects.all().order_by('name')
        if(not response.get('Group')):
            groupsID=''
        else:
            groupsID=response['Group']
        return render_to_response( 'staff/create.html',{'staff': request.user.staff,'RoleList' : lContestEvents,'GroupList':lContestEventsGroup,
                                                        'username':response['UserName'][0].strip(),'name':response['RealName'][0].strip(),
                                                        'girl':not int(response['Gender'][0].strip()),'groupsID':groupsID,
                                                        'roleID':int(response['Role'][0].strip()),'content':response['Remark'][0].strip()},context)
    else:
        lContestEvents = Role.objects.exclude(name="admin").order_by('name')
        lContestEventsGroup = Group.objects.all().order_by('name')
        ngroup = Staff.objects.filter(group=None)
        return render_to_response( 'staff/create.html',{'staff': request.user.staff,'RoleList' : lContestEvents,'GroupList':lContestEventsGroup,'group':lContestEventsGroup,'ngroup':ngroup},context)

#@login_required(login_url="/app/login/")
#@permission_required_with('staff')
def createStaff(request):
    """
    add a staff
    """
    if request.method=="POST":
        myDict = dict(request.POST.iterlists())
        userName=myDict['UserName'][0].strip()
        passWord=myDict['Password'][0].strip()
        passWord2=myDict['Password2'][0].strip()
        realName=myDict['RealName'][0].strip()
        content=myDict['Remark'][0].strip()
        gender=int(myDict['Gender'][0].strip())
        groupList=request.POST.getlist('Group')
        calendarDispList=request.POST.getlist('setCalendarDisp')
        if(userName==''):# info error
            messages.error(request, '用户名不能为空')
            return False,myDict
        if(len(userName)>50):# info error
            messages.error(request, '用户名不能大于50个字符')
            return False,myDict
        if(passWord==''):# info error
            messages.error(request, '密码不能为空')
            return False,myDict
        if(realName==''):# info error
            messages.error(request, '姓名不能为空')
            return False,myDict
        if(len(realName)>50):# info error
            messages.error(request, '姓名不能大于50个字符')
            return
        if(passWord!=passWord2):# info error
            messages.error(request, '两次密码输入不一致')
            return False,myDict
        if(User.objects.filter(username=userName).count()!=0):#same user
            messages.error(request, '用户名已存在')
            return False,myDict
        if(Staff.objects.filter(name=realName).count()!=0):#same realName
            messages.error(request, '姓名已存在')
            return False,myDict
        if(not myDict.get('Role')):
            messages.error(request, '权限不能为空')
            return False,myDict
        roleID=myDict['Role'][0].strip()
        md5Password=hashlib.md5(passWord).hexdigest()[8:-8]
        user=User(username=userName,password=md5Password)
        #user.set_password(user.password)#hash password
        #password = make_password(passWord,'md5')
        user.save()
        role =Role.objects.get(id=roleID)
        mS=Staff(user=user,name=realName,role=role,gender=gender,content=content)
        mS.save()
        if(groupList!=''):
            for groupItem in groupList:
                g=Group.objects.get(id=groupItem)
                mS.group.add(g)
        if(calendarDispList!=''):
            for staffID in calendarDispList:
                staff=Staff.objects.get(id=int(staffID))
                mS.visibleStaff.add(staff)
        mS.visibleStaff.add(mS)
        mS.save()
        cache.clear()
        messages.success(request, '添加成功')
    return True,''

#@login_required(login_url='/app/login/')
#@permission_required_with('staff')
def getVisibleStaff():

    """
    return visible staff
    """
    return Staff.objects.filter(visible=True).order_by('name')

@login_required(login_url="/app/login/")
@permission_required_with('staff')
def show(request):
    """
    show the show staff html
    """
    context = RequestContext(request)
    showSave(request)
    showDelete(request)
    result,response=showEdit(request)
    if result:
        return response
    lContestEvents = Staff.objects.exclude(user__username="admin").order_by('role__name','name')
    lContestEventsGroup = Group.objects.all().order_by('name')
    return render_to_response('staff/show.html',{'StaffList':lContestEvents,'GroupList':lContestEventsGroup,'staff':request.user.staff},context)

#@login_required(login_url="/app/login/")
#@permission_required_with('staff')
def showSave(request):
    """
    save the show
    """
    if request.method=="POST":
        myDict = dict(request.POST.iterlists())
        if(not myDict.get('StaffSave')):
            return
        staffID=myDict['StaffSave'][0]
        if(myDict.get('editVisible'+staffID)):
            editVisible=True
        else:
            editVisible=False
        Staff.objects.filter(id=staffID).update(visible=editVisible)
        cache.clear()
        messages.success(request, '修改成功')

#@login_required(login_url="/app/login/")
#@permission_required_with('staff')
def showEdit(request):
    """
    show the edit staff html
    """
    context = RequestContext(request)
    showEditSave(request)
    if request.method=="POST":
        myDict = dict(request.POST.iterlists())
        if(myDict.get('StaffEdit')):
            staffID=myDict['StaffEdit'][0]
        elif(myDict.get('editStaffSave')):
            staffID=myDict['editStaffSave'][0]
        else:
            return False,''
        lContestEvents = Staff.objects.get(id=staffID)
        lContestEventsRole = Role.objects.exclude(name="admin").order_by('name')
        lContestEventsGroup = Group.objects.all().order_by('name')
        ngroup = Staff.objects.filter(group=None)
        return True,render_to_response('staff/edit.html',{'staff': request.user.staff,'Staff':lContestEvents,'RoleList':lContestEventsRole,'GroupList':lContestEventsGroup,'group':lContestEventsGroup,'ngroup':ngroup},context)
    return False,''

#@login_required(login_url="/app/login/")
#@permission_required_with('staff')
def showEditSave(request):
    """
    save the edit
    """
    if request.method=="POST":
        myDict = dict(request.POST.iterlists())
        if(not myDict.get('editStaffSave')):
            return
        staffID=myDict['editStaffSave'][0].strip()
        userName=myDict['UserName'][0].strip()
        passWord=myDict['Password'][0].strip()
        passWord2=myDict['Password2'][0].strip()
        realName=myDict['RealName'][0].strip()
        content=myDict['Remark'][0].strip()
        roleID=myDict['Role'][0].strip()
        gender=int(myDict['Gender'][0].strip())
        groupList=request.POST.getlist('Group')
        calendarDispList=request.POST.getlist('setCalendarDisp')
        srcUserName=Staff.objects.get(id=staffID).user.username
        srcRealName=Staff.objects.get(id=staffID).name
        if(userName==''):# info error
            messages.error(request, '用户名不能为空')
            return
        if(len(userName)>50):# info error
            messages.error(request, '用户名不能大于50个字符')
            return
        if(passWord==''):# info error
            messages.error(request, '密码不能为空')
            return
        if(realName==''):# info error
            messages.error(request, '姓名不能为空')
            return
        if(len(realName)>50):# info error
            messages.error(request, '姓名不能大于50个字符')
            return
        if(passWord!=passWord2):# info error
            messages.error(request, '两次密码输入不一致')
            return
        if(srcUserName!=userName and User.objects.filter(username=userName).count()!=0):#same user
            messages.error(request, '用户名已存在')
            return
        if(srcRealName!=realName and Staff.objects.filter(name=realName).count()!=0):#same name
            messages.error(request, '姓名已存在')
            return
        user=Staff.objects.get(id=staffID).user
        userID=user.id
        if(user.password!=passWord):
            md5Password = hashlib.md5(passWord).hexdigest()[8:-8]
        else:
            md5Password=passWord
        User.objects.filter(id=userID).update(username=userName,password=md5Password)
        roleInfo = Role.objects.get(id=roleID)
        mS=Staff.objects.get(id=staffID)
        mS.name=realName
        mS.role=roleInfo
        mS.gender=gender
        mS.content=content
        mS.group.clear()
        if(groupList!=''):
            for groupItem in groupList:
                g=Group.objects.get(id=groupItem)
                mS.group.add(g)
        mS.visibleStaff.clear()
        if(calendarDispList!=''):
            for staffID in calendarDispList:
                staff=Staff.objects.get(id=int(staffID))
                mS.visibleStaff.add(staff)
        mS.visibleStaff.add(mS)
        mS.save()
        cache.clear()
        messages.success(request, '修改成功')

#@login_required(login_url="/app/login/")
#@permission_required_with('staff')
def showDelete(request):
    """
    show the edit staff html
    """
    if request.method=="POST":
        myDict = dict(request.POST.iterlists())
        if(not myDict.get('StaffDelete')):
            return
        staffID=myDict['StaffDelete'][0]
        userID=Staff.objects.get(id=staffID).user.id
        Staff.objects.get(id=staffID).group.clear()
        Staff.objects.get(id=staffID).delete()
        User.objects.get(id=userID).delete()
        cache.clear()
        messages.success(request, '删除成功')

@login_required(login_url="/app/login/")
@permission_required_with('staff')
def group(request):
    """
    show the group html
    """
    context = RequestContext(request)
    groupDelete(request)
    groupAdd(request)
    result2,response2=groupEdit(request)
    if result2:
        return response2
    lContestEvents = Group.objects.all().order_by('name')
    return render_to_response('staff/group.html',{'GroupList' : lContestEvents,'StaffList' : getVisibleStaff(),'staff':request.user.staff},context)

#@login_required(login_url="/app/login/")
#@permission_required_with('staff')
def groupEdit(request):
    """
    Edit group
    """
    context = RequestContext(request)
    groupEditSave(request)
    if request.method=="POST":
        myDict = dict(request.POST.iterlists())
        if(myDict.get('EditGroup')):
            groupID=int(myDict['EditGroup'][0])
        elif(myDict.get('editGroupSave')):
            groupID=int(myDict['editGroupSave'][0])
        else:
           return False,''
        lContestEvents = Group.objects.get(id=groupID)
        return True,render_to_response('staff/groupEdit.html',{'staff': request.user.staff,'Group':lContestEvents,'StaffList' : getVisibleStaff()},context)
    return False,''

#@login_required(login_url="/app/login/")
#@permission_required_with('staff')
def groupEditSave(request):
    """
    save the Group edit
    """
    if request.method=="POST":
        myDict = dict(request.POST.iterlists())
        if(not myDict.get('editGroupSave')):
            return
        groupID=int(myDict['editGroupSave'][0])
        name=myDict['GroupName'][0].strip()
        content=myDict['GroupRemark'][0].strip()
        srcName=Group.objects.get(id=groupID).name
        if(name==''):
            messages.error(request, '组名不能为空')
            return
        if(srcName!=name and Group.objects.filter(name=name).count()!=0):
            messages.error(request, '组名已存在')
            return
        mG=Group.objects.get(id=groupID)
        mG.name=name
        mG.content=content
        if(myDict.get('GroupLeader')):
            leaderID=myDict['GroupLeader'][0]
            leader=Staff.objects.get(id=leaderID)
            mG.leader=leader
            mG.save()
        else:
            mG.leader=None
        if(myDict.get('GroupMember')):
            mG.member.clear()
            selectMem=myDict.get('GroupMember')
            for mem in selectMem:
               staff=Staff.objects.get(id=mem)
               mG.member.add(staff)
               mG.save()
        else:
            mG.member.clear()
        mG.save()
        cache.clear()
        messages.success(request, '修改成功')

#@login_required(login_url="/app/login/")
#@permission_required_with('staff')
def groupDelete(request):
    """
    delete group
    """
    if request.method=="POST":
        myDict = dict(request.POST.iterlists())
        if(not myDict.get('DeleteGroup')):
            return
        id=int(myDict['DeleteGroup'][0])
        Group.objects.get(id=id).member.clear()
        Group.objects.get(id=id).delete()
        cache.clear()
        messages.success(request, '删除成功')

#@login_required(login_url="/app/login/")
#@permission_required_with('staff')
def groupAdd(request):
    """
    add group
    """
    if request.method=="POST":
        myDict = dict(request.POST.iterlists())
        if(not myDict.get('AddGroup')):
            return
        name=myDict['EditGroupName'][0].strip()
        if(name==''):
            messages.error(request, '组名不能为空')
            return
        if(Group.objects.filter(name=name).count()!=0):
            messages.error(request, '组名已存在')
            return
        mG=Group(name=name)
        if(myDict.get('EditGroupMember')):
            leaderID=myDict['EditLeaderID'][0]
            leader=Staff.objects.get(id=leaderID)
            mG.leader=leader
            mG.save()
            selectMem=myDict.get('EditGroupMember')
            for mem in selectMem:
               staff=Staff.objects.get(id=mem)
               mG.member.add(staff)
        mG.save()
        cache.clear()
        messages.success(request, '添加成功')

@login_required(login_url="/app/login/")
@permission_required_with('staff')
def role(request):
    """
    show the auth html
    """
    context = RequestContext(request)
    roleAdd(request)
    roleEdit(request)
    roleDelete(request)
    lContestEvents = Role.objects.exclude(name="admin").order_by('name')
    lContestEventsLevel=[i+1 for i in range(10)]
    staff = request.user.staff
    return render_to_response( 'staff/role.html',{'staff':staff,'RoleList' : lContestEvents,'LevelList':lContestEventsLevel,'exportFile':request.user.staff.role.exportFile},context)

#@login_required(login_url="/app/login/")
#@permission_required_with('staff')
def roleAdd(request):
    """
    save the role
    """
    if request.method=="POST":
        myDict = dict(request.POST.iterlists())
        if(not myDict.get('addRole')):
            return
        editStaff=False
        editTask=False
        editCalendar=False
        editMeeting=False
        exportFile=False
        editName=myDict['editName'][0].strip()
        if (myDict.get('editLevel')):
            editLevel=['editLevel'][0]
        else:
            editLevel=5
        if(editName==''):
            messages.error(request, '权限名不能为空')
            return
        if(Role.objects.filter(name=editName).count()!=0):
            messages.error(request, '权限名已存在')
            return
        if(myDict.get('editStaff')):
            editStaff=True
        if(myDict.get('editTask')):
            editTask=True
        if(myDict.get('editCalendar')):
            editCalendar=True
        if(myDict.get('editMeeting')):
            editMeeting=True
        if(myDict.get('exportFile')):
            exportFile=True
        Role.objects.create(name=editName,level=editLevel,editStaff=editStaff,editTask=editTask,editCalendar=editCalendar,editMeeting=editMeeting,exportFile=exportFile)
        cache.clear()
        messages.success(request, '添加成功')

#@login_required(login_url="/app/login/")
#@permission_required_with('staff')
def roleEdit(request):
    """
    edit the role
    """

    if request.method=="POST":
        myDict = dict(request.POST.iterlists())
        if(not myDict.get('editRole')):
            return
        editStaff=False
        editTask=False
        editCalendar=False
        editMeeting=False
        exportFile=False
        roleID=myDict['editRole'][0]
        editName=myDict['editName'+roleID][0].strip()
        srcName=Role.objects.get(id=roleID).name
        if(myDict.get('editLevel'+roleID)):
            editLevel=myDict['editLevel'+roleID][0]
        else:
            editLevel=5
        if(editName==''):
            messages.error(request, '权限名不能为空')
            return
        if(editName!=srcName and  Role.objects.filter(name=editName).count()!=0):
            messages.error(request, '权限名已存在')
            return
        if(myDict.get('editStaff'+roleID)):
            editStaff=True
        if(myDict.get('editTask'+roleID)):
            editTask=True
        if(myDict.get('editCalendar'+roleID)):
            editCalendar=True
        if(myDict.get('editMeeting'+roleID)):
            editMeeting=True
        if(myDict.get('exportFile'+roleID)):
            exportFile=True
        mR=Role.objects.get(id=roleID)
        mR.name=editName
        mR.level=editLevel
        mR.editStaff=editStaff
        mR.editCalendar=editCalendar
        mR.editTask=editTask
        mR.editMeeting=editMeeting
        mR.exportFile=exportFile
        mR.save()
        messages.success(request, '修改成功')
        cache.clear()

#@login_required(login_url="/app/login/")
#@permission_required_with('staff')
def roleDelete(request):
    """
    delete the role
    """
    if request.method=="POST":
        myDict = dict(request.POST.iterlists())
        if(not myDict.get('deleteRole')):
            return
        roleID=myDict['deleteRole'][0]
        mR=Role.objects.get(id=roleID)
        if(mR.name=='默认权限'):
            mR.editCalendar=False
            mR.editMeeting=False
            mR.editStaff=False
            mR.editTask=False
            mR.exportFile=False
            mR.level=5
            mR.save()
            messages.success(request, '删除成功')
            return
        if(Role.objects.filter(name='默认权限').count()==1):
            minR=Role.objects.get(name='默认权限')
        else:
            minR=Role(name='默认权限',level=5,editStaff=False,editTask=False,editCalendar=False,editMeeting=False,exportFile=False)
        minR.save()
        for item in mR.staff.all():
            item.role=minR
            item.save()
        mR.delete()
        cache.clear()
        messages.success(request, '删除成功')




