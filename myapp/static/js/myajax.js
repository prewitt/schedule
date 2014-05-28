$(document).ready(function() {

    $(".toTop").off("click");
    $(document).on('click', '.toTop', function(){
        //alert("top");
        window.scrollTo(0, 0);
    });

    //special for reset button click
    $('.back_button').off('click');
    $(document).on('click','.back_button',function(){
        //console.log('aa');
        id=$(this).attr('iid');
        alert($("#"+id));
        $("#" + id).trigger("click");
        return false;

    });

    //for sidebar class="get_method"
    $('.get_method').off('click');
    $(document).on('click','.get_method',function(){

        $('.nav li').removeClass('active');
        $(this).parent().addClass('active');
        //alert('ha');
        $.get($(this).attr('url'),function(data){
            //  alert(data);
            clearFun();
            $('#content div').empty();
            $('#first').empty().html(data);
        });
        return true;
    });

    //for sidebar class="which_select"
//    $('.which_select').off('click');
//    $(document).on('click','.which_select',function(){
//
//        $('.nav li').removeClass('active');
//        $(this).parent().addClass('active');
//        return true;
//    });

    //for affirm and submit button in task management
    $('.task_state_button').off('click');
    $(document).on('click','.task_state_button',function(){
        $.get($(this).attr('url'),function(data){
            clearFun();
            $('#content div').empty();
            $('#first').empty().html(data);
        });
        return false;
    });

    $('.get_others_calendar').off('click');
    $(document).on('click','.get_others_calendar',function(){
        $.get($(this).attr('url'),function(data){
            $('#third').empty().html(data);
        });
        return true;
    });


    //for edit/delete task button
    $('#edit_task_button').off('click');
    $(document).on('click','#edit_task_button',function(){
        $.get($(this).attr('url'),function(data){
            //  alert(data);
            clearFun();
            $('#content div').empty();
            $('#first').empty().html(data);
        }) ;
        return false;
    });
    var task_url='';
    $('.task_button').off('click');
    $(document).on('click','.task_button',function(){
        task_url=$(this).attr('url');
        //return false;
    });

    $(document).on('submit','.task_submit_form',function(){
        //alert('submit');
        $.ajax({
            type:$(this).attr('method'),
            url:task_url,
            data:'',
            success:function(data){
                //alert(data);
                clearFun();
                $('#content div').empty();
                $('#first').empty().html(data);
            }
        });
        return false;
    });

    //for all class="submit_form"
    $(document).on('submit','.submit_form',function(){

        $.ajax({
            type:$(this).attr('method'),
            url:$(this).attr('action'),
            data:$(this).serialize(),
            success: function(data){
                //alert(data);
//                clearFun();
//                $('#content div').empty();
                $('#first').empty().html(data);
            }
        });
        return false;
    });
    //for all class="add_task_form"
    $(document).on('submit','.add_task_form',function(){

        $(".add_tsk").attr("disabled","true");

        $.ajax({
            type:$(this).attr('method'),
            url:$(this).attr('action'),
            data:$(this).serialize(),
            success: function(data){
                //alert(data);
                clearFun();
                $('#content div').empty();
                $('#first').empty().html(data);
            }
        });
        return false;
    });

    //for comment form
    $(document).on('submit','.submit_comment_form',function(){

        $.ajax({
            type:$(this).attr('method'),
            url:$(this).attr('action'),
            data:$(this).serialize(),
            success: function(data){
                clearFun();
                //$('#content div').empty();
                $('#second').empty().html(data);
            }
        });
        return false;
    });


    //special for staff form submit
    var staff_submit_name="";
    var staff_submit_value="";
    $('.staff_button').off('click');
    $(document).on('click','.staff_button',function(){
        staff_submit_name= $(this).attr('name');
        staff_submit_value= $(this).attr('value');
        //alert(staff_submit_name);
        //return false;
    });

    $(document).on('submit','.staff_submit_form',function(){
        var my_data = $(this).serialize()+'&'+staff_submit_name+"="+staff_submit_value;
        //alert(my_data);
        $.ajax({
            type:$(this).attr('method'),
            url:$(this).attr('action'),
            data:my_data,
            success: function(data){
                //alert(data);
                clearFun();
                $('#content div').empty();
                $('#first').empty().html(data);

            }
        });
        return false;
    });
    //special for notice and meeting form delete submit
    var delete_id="";
    $('.delete_button').off('click');
    $(document).on('click','.delete_button',function(){
        //alert('a');
        delete_id= $(this).attr('name');
    });
    $(document).on('submit','.delete_submit_form',function(){

        var my_data = $(this).serialize()+'&delete_id='+delete_id;
        $.ajax({
            type:$(this).attr('method'),
            url:$(this).attr('action'),
            data:my_data,
            success: function(data){
                //alert(data);
                clearFun();
                $('#content div').empty();
                $('#first').empty().html(data);
            }
        });
        return false;
    });
    //special for notice and meeting detail
    $('.detail_button').off('click');
    $(document).on('click','.detail_button',function(){
        $.get($(this).attr('url'),function(data){
            //alert(data);
            $('#second').empty().html(data);
        });
        return true;
    });

    $('.back_calendar_button').off('click');
    $(document).on('click','.back_calendar_button',function(){
        $.get($(this).attr('url'),function(data){
            //alert(data);
            clearFun();
            $('#content div').empty();

            $('#third').empty().html(data);
        });
    });

    //special for calendar form submit
    var dayitems_submit_name="";
    var dayitems_submit_value="";
    $(document).on('click','.dayitems_button',function(){
        dayitems_submit_name= $(this).attr('name');
        dayitems_submit_value= $(this).attr('value');
        //$(".get_method_for_calendar").trigger("click");

    });

    //calendar
    $(document).on('click','.get_others_calendar',function(){
        $.get($(this).attr('url'),function(data){
            $('#third').empty().html(data);
        });
        return false;
    });
    //submit_dayitems_form
    $(document).on('submit','.submit_dayitems_form',function(){
        var my_data = $(this).serialize()+'&'+dayitems_submit_name+"="+dayitems_submit_value;
        var my_url=$(this).attr('url');
        $.ajax({
            type:$(this).attr('method'),
            url:$(this).attr('action'),
            data:my_data,
            success: function(data){
                //$("#manage_calendar").click();
                $('#fourth').empty().html(data);
                $.get(my_url,function(my_data){
                    //  alert(data);
                    $('#first').empty();
                    $('#second').empty();
                    $('#third').empty().html(my_data);
                    //$('#four').html('aa');
                });
            }
        });
        //$(".get_method_for_calendar").trigger("click");
        return false;
    });
    // clear_button in calendar
    $(document).on('click','.clear_fourth_button',function(){
        $('#fourth').empty();
        return false;
    });
    $(document).on('click','.clear_third_button',function(){
        $('#fourth').empty();
        $('#third').empty();
        return false;
    });
    $(document).on('click','.clear_second_button',function(){
        $('#fourth').empty();
        $('#third').empty();
        $('#second').empty();
        return true;
    });

    $(document).on('click','.clear_task_node_detail',function(){
        var id=$(this).attr('id');
        $('#task_node_'+id).empty();
        return true;
    });

    //for sidebar id="manage_calendar"
    $(document).on('click','#manage_calendar',function(){

        $('.nav li').removeClass('active');
        $(this).parent().addClass('active');
        //alert('ha');
        $.get($(this).attr('url'),function(data){
            //  alert(data);
            clearFun();
            $('#content div').empty();
            $('#third').empty().html(data);
        });
        return true;
    });

    //for sidebar id="show_calendar"
    $(document).on('click','#show_calendar',function(){

        $('.nav li').removeClass('active');
        $(this).parent().addClass('active');
        //alert('ha');
        $.get($(this).attr('url'),function(data){
            //  alert(data);
            clearFun();
            $('#content div').empty();
            $('#first').empty().html(data);
        });
        return true;
    });
    //calendar
    $(document).on('click','.get_calendar',function(){
        $.get('/calendar/'+StaffID+'/',function(data){
            clearFun();
            $('#content div').empty();
            $('#third').empty().html(data);
        });
    });
    $(document).on('click','#get_calendar_now',function(){
        $.get('/calendar/'+StaffID+'/',function(data){
            //$('#content div').empty();
            $('#third').empty().html(data);
        });
        return false;
    });
    $(document).on('click','#get_year_before_calendar',function(){
        $.get('/calendar/'+YearBeforeThis+'/'+Month+'/'+StaffID+'/',function(data){
            //$('#content div').empty();
            $('#third').empty().html(data);
        });
        return false;
    });
    $(document).on('click','#get_previous_month_calendar',function(){
        $.get('/calendar/'+PreviousYear+'/'+PreviousMonth+'/'+StaffID+'/',function(data){
            //$('#content div').empty();
            $('#third').empty().html(data);
        });
        return false;
    });
    $(document).on('click','#get_next_month_calendar',function(){
        $.get('/calendar/'+NextYear+'/'+NextMonth+'/'+StaffID+'/',function(data){
            //$('#content div').empty();
            $('#third').empty().html(data);
        });
        return false;
    });
    $(document).on('click','#get_year_after_calendar',function(){
        $.get('/calendar/'+YearAfterThis+'/'+Month+'/'+StaffID+'/',function(data){
            //$('#content div').empty();
            $('#third').empty().html(data);
        });
        return false;
    });
    $(document).on('click','.get_day_items',function(){
        var year=$(this).find('.get_day_items_div').attr('year');
        var month=$(this).find('.get_day_items_div').attr('month');
        var day=$(this).find('.get_day_items_div').attr('day');
        var id=$(this).find('.get_day_items_div').attr('id');
        $("#calendar tbody tr td").removeClass("selected");
        $(this).addClass('selected');
        $.get('/calendar/'+year+'/'+month+'/'+day+'/'+id+'/',function(data){
            //$('#content div').empty();
            $('#fourth').empty().html(data);
        });
        if(id=='0')
        {
            $('body,html').animate({scrollTop:0},20);
        }
        else
        {
            $('body,html').animate({ scrollTop: $(".myCalendar").offset().top-50}, 20);
        }
    });

    function clearFun(){
        $('.table_show_detail').unbind();
        $(".table_show_detail thead input").unbind();
        $('#time_start1').unbind();
        $('#time_end1').unbind();
        $('#time_start2').unbind();
        $('#time_end2').unbind();
        $('.table_show').unbind();

        $('.modalLink').unbind();
        $("#m_radio_OK").unbind();
        $("#m_checkbox_OK").unbind();
        $("#m_checkbox_Close").unbind();


        $("#finish").unbind();
        $("#temp").unbind();
        $("#reset").unbind();

        $("#taskTree").unbind();
        $('#detail').unbind();
        $('#createTemp').unbind();
        $('#search_q').unbind();
        $("#taskTempsTree").unbind();
        $('#delTemp').unbind();
        $('#delete').unbind();
    }

    $(document).on('click','.get_comments',function(){
            task_id = $(this).attr('task_id');
            url = "/task/get_comments/"+task_id;
      //alert(url);
            $.ajax({
                type:"GET",
                url:url,
                success: function(data){
                    //alert(data);
                    $("#comment_"+task_id).empty().html(data);
                    $("#comment_detail_"+task_id).empty().html(data);
                }
            });
            return true;
        });
    $(document).on('click','.get_feedbacks',function(){
            task_id = $(this).attr('task_id');
            url = "/task/get_feedbacks/"+task_id;
            $.ajax({
                type:"GET",
                url:url,
                success: function(data){
                    $("#feedback_"+task_id).empty().html(data);
                }
            });
            return true;
        });
       $(document).on('submit','.form_comment',function(){
        url=$(this).attr("action");
        $.ajax({
                type:"POST",
                url:url,
                data:$(this).serialize(),
                success: function(data){
                    alert(data);
                }
        });
        $('.closeBtn').click();
        return false;
        });

    //////////////////////////////////////////Bug
        $(document).on('click','.get_comments_bug',function(){
            bug_id = $(this).attr('bug_id');
            url = "/bug/get_comments/"+bug_id;
        //alert(url);
            $.ajax({
                type:"GET",
                url:url,
                success: function(data){
                    //alert(data);
                    $("#comment_"+bug_id).empty().html(data);
                    $("#comment_detail_"+bug_id).empty().html(data);
                }
            });
            return true;
        });
    $(document).on('click','.get_feedbacks_bug',function(){
            bug_id = $(this).attr('bug_id');
            url = "/bug/get_feedbacks/"+bug_id;
            $.ajax({
                type:"GET",
                url:url,
                success: function(data){
                    $("#feedback_"+bug_id).empty().html(data);
                }
            });
            return true;
        });
       $(document).on('submit','.form_comment_bug',function(){
        url=$(this).attr("action");
        $.ajax({
                type:"POST",
                url:url,
                data:$(this).serialize(),
                success: function(data){
                    alert(data);
                }
        });
        $('.closeBtn').click();
        return false;
       });

    $('.popup').click(function(event) {
    event.preventDefault();
    window.open($(this).attr("href"), "popupWindow", "width=600,height=600,scrollbars=yes");
});

});