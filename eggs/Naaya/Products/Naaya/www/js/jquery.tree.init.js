$(document).ready(function(){
    $(TREE_CONTAINER).tree({
        data:{
            type : "json",
            opts : {
                url : TREE_GET_URL
            }
        },
        callback : {
            onload: function(TREE_OBJ){
                TREE_OBJ.opened_nodes = []
                $.each(TREE_OBJ.container.children().children(), function(i, node){
                    TREE_OBJ.opened_nodes.push(node)
                    TREE_OBJ.open_branch(node); //Opening first level of the site
                })
            },
            onopen: function(NODE, TREE_OBJ){
                if ($.inArray(NODE, TREE_OBJ.opened_nodes) == -1){//Reload
                    TREE_OBJ.opened_nodes.push(NODE)
                    $.getJSON(TREE_GET_URL+'?node=' + $(NODE).attr('title'), function(data){
                        $.each($(NODE).children().children('li'), function(i, node){
                            TREE_OBJ.remove(node);
                        })
                        $.each(data, function(i, node_data){
                            TREE_OBJ.create(node_data, $(NODE), 'inside')
                        })
                    })
                }
            },
            onselect: function(NODE, TREE_OBJ){
                // If the tree_container has xxx_tree id the target input should have xxx_tree_target class
                target = $('.' + TREE_OBJ.container.attr('id') + '_target')
                if (target.length){
                    val = $(NODE).attr('title')
                    if (val == '/')
                        target.val(val)
                    else //Search first / then substr from it's position
                        target.val(val.substring(val.indexOf('/')+1, val.length));
                }
                else
                    alert('Error: Please set up the target input class');
            }
        },
        types : {
            "default" : {
                draggable: false
            }
        }
   })
})
