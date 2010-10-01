/**
 * All the utility functions used in the admin sections
*/
$(document).ready(function(){
    $('.autocomplete').each(function(){
        var source = $(this).parents('form').attr('href').
        replace(/http:\/\/[^\/]+\//, '');
        var template = $('#template').val();
        var content;

        var self = $(this)

        self.autocomplete({
            minLength: 3,
            delay: 500,
            source: function(request, response) {
                toggleLoader();
                var search_query = window.location.search;
                if (search_query[0] == '?'){ //remove first ?
                    search_query = search_query.substr(1);
                }
                data = unserialize(search_query); //utils.js
                data['query']=request.term;
                data['template'] = template;
                data['role'] = $('#filter-roles').val();
                if($('#all_users').length){
                    data['all_users'] = $('#all_users').val();
                }
                $.get(source, data, function(data){
                    $('.datatable').replaceWith(data);
                    toggleLoader();
                });
			}
        });

        self.keyup(function(keyCode){
            if($(this).val() == ''){
                $(this).autocomplete("search", '   ');
            }
        });

        $('#filter-roles').change(function(e){
            self.autocomplete('search', '   ');
        });
    });
    add_onclick_second_tabs();
    add_onclick_sort_links();
    add_onclick_group_links();
});
function toggleLoader(){
    $('.ajax-loader').toggle();
    if ($('#autocomplete-query').attr("disabled") === true){
        $('#autocomplete-query').attr("disabled", "");
        $('#autocomplete-query').focus();
    }else{
        $('#autocomplete-query').attr("disabled", "disabled");
    }
}

function emptyLocation(){
   if (document.forms['frmUsersRoles'].loc[0].checked == true)
       document.forms['frmUsersRoles'].location.value = '';
}

function pickLocation(){
   document.forms['frmUsersRoles'].loc[1].checked = true;
}

function setupWin(url, theWidth, theHeight){
   pickLocation();
   wwinn=window.open(url,'wwinn','width='+theWidth+',height='+theHeight+',scrollbars,top=50,left=600');
   wwinn.focus();
   return true;
}

function createKey(key){
   document.forms['frmUsersRoles'].location.value = key;
}

/**
 * Functions for LDAPUserFolder
*/
function select_second_tab(tabid) {
    $('.second_tab_set a.current_sub').removeClass('current_sub');
    if (tabid) {
        $('#'+tabid).addClass('current_sub');
    }
}

function add_onclick_sort_links() {
    $('.sort_link').click(function() {
        show_ldap_users_fieldset($(this).attr('href'));
        return false;
    });
}

function add_onclick_second_tabs() {
    $('.second_tab').click(function() {
        show_ldap_section($(this).attr('id'), $(this).attr('href'));
        return false;
    });
}

function add_onclick_group_links() {
    $('.group_link').click(function() {
        show_ldap_section('', $(this).attr('href'));
        return false;
    });
}

function ajax_user_search_form() {
    $('#frmRoles').ajaxForm({
    beforeSubmit: function() {
        $('#waiting_for_search_results').show();
        $('#search_results_parent').hide();
    },
    success: function(data) {
        var html = $("#search_results_parent", $(data)).html();
        $('#search_results_parent').html(html);

        $('#waiting_for_search_results').hide();
        $('#search_results_parent').show();
    },
    error: function() {
        $('#error_on_search_results').show();
        $('#waiting_for_search_results').hide();
    }
    });
}

function show_ldap_section(tabid, url) {
    select_second_tab(tabid);

    $('#section_wating_response').show();
    $('#section_parent').hide();

    $.ajax({
        url: url,
        success: function(data) {
            var html = $("#section_parent", $(data)).html();
            $('#section_parent').html(html);

            if (tabid == 'link_manage_all') {
                add_onclick_sort_links();
                add_onclick_group_links();
            } else if (tabid == 'link_assign_to_users') {
                ajax_user_search_form();
            }

            $('#section_wating_response').hide();
            $('#section_parent').show();
        },
        error: function() {
            $('#section_wating_response').hide();
            $('#section_error_response').show();
        }
    });
}

function show_ldap_users_fieldset(url) {
    $('#users_roles_wating_response').show();

    $.ajax({
        url: url,
        success: function(data) {
            var html = $("#users_field", $(data)).html();
            $('#users_field').html(html);

            add_onclick_sort_links();

            $('#users_roles_wating_response').hide();
        },
        error: function() {
            $('#users_roles_wating_response').hide();
            $('#users_roles_error_response').show();
        }
    });
}
/**
 * End Functions for LDAPUserFolder
*/
