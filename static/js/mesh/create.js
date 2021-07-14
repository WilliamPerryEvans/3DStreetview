// use bathymetry_edit.js as example for form capture and submit after other stuff
function get_odk_projects()
{
    // get current id of mesh
//    const id = $('input#mesh_id').val();
    const odkconfig_id = $('#odk_config').val();
    document.getElementById("odk_project_create").disabled = true;
    document.getElementById("odk_project_delete").disabled = true;
    // clear current projects in dropdown
    var project_select = document.getElementById("odk_project");
    removeOptions(project_select);
    addDisabledOption(project_select);
    $.getJSON(
        `/api/odk/${odkconfig_id}/projects`,
        function(data) {
            console.log(data);
            // populate the project dropdown with results
            data.forEach(function(x) {
                var option = document.createElement("option");
                option.text = x.name;
                option.value = x.id;
                project_select.add(option);
            });
            flashMessage([{"type": "success", "message": "Server found"}]);
            document.getElementById("odk_project_create").disabled = false;
            document.getElementById("odk_project_delete").disabled = false;

        }
    )
    .fail(function() {
        // flash a message in case everything fails
        flashMessage([{"type": "danger", "message": "Server not available"}]);
    });
};


function get_odm_projects()
{
    // get current id of mesh
//    const id = $('input#mesh_id').val();
    const odmconfig_id = $('#odm_config').val();
    document.getElementById("odm_project_create").disabled = true;
    document.getElementById("odm_project_delete").disabled = true;
    // clear current projects in dropdown
    var project_select = document.getElementById("odm_project");
    removeOptions(project_select);
    addDisabledOption(project_select);
    $.getJSON(
        `/api/odm/${odmconfig_id}/projects`,
        function(data) {
            // populate the project dropdown with results
            console.log(data.results)
            data.results.forEach(function(x) {
                var option = document.createElement("option");
                option.text = x.name;
                option.value = x.id;
                project_select.add(option);
            });
            flashMessage([{"type": "success", "message": "Server found"}]);
            document.getElementById("odm_project_create").disabled = false;
            document.getElementById("odm_project_delete").disabled = false;

        }
    )
    .fail(function() {
        // flash a message in case everything fails
        flashMessage([{"type": "danger", "message": "Server not available"}]);
    });
};

function save_odm_project() {
    const id = $('input#mesh_id').val();
    const odmconfig_id = $('#odm_config').val();
    console.log(id);
    console.log(odmconfig_id);
    name = document.getElementById("odm_project_name").value;
    desc = document.getElementById("odm_project_desc").value;
    content = {
        "name": name,
        "description": desc
    }
    $.ajax({
        type: 'POST',
        url: `/api/odm/${odmconfig_id}/projects/`,
        data: JSON.stringify(content),
        contentType: "application/json",
        dataType: 'json',
        // Submit parent form on success.
        success: function(data) {
            console.log(data);
            // refresh project list
            get_odm_projects();
            $('#newOdmProject').modal('hide');
            flashMessage([{"type": "success", "message": "New ODM project created"}]);

        },
        // Enable save button again.
        error: function() { flashMessage([{"type": "danger", "message": "Not able to create ODM project"}]) }
    });
}

function save_odk_project() {
    const id = $('input#mesh_id').val();
    const odkconfig_id = $('#odk_config').val();
    console.log(id);
    console.log(odkconfig_id);
    name = document.getElementById("odk_project_name").value;
    content = {
        "name": name,
    }
    $.ajax({
        type: 'POST',
        url: `/api/odk/${odkconfig_id}/projects/`,
        data: JSON.stringify(content),
        contentType: "application/json",
        dataType: 'json',
        // Submit parent form on success.
        success: function(data) {
            console.log(data);

            $.ajax({
                type: 'POST',
                url: `/api/odk/${odkconfig_id}/projects/${data.id}/app-users`,
                data: JSON.stringify({"displayName": "Surveyor"}),
                contentType: "application/json",
                dataType: 'json',
                // Submit parent form on success.
                function(app_user) {
                    console.log(app_user);
                }
            });
            // refresh project list
            get_odk_projects();
            $('#newOdkProject').modal('hide');
            flashMessage([{"type": "success", "message": "New ODK project created"}]);
        },
        // Enable save button again.
        error: function() { flashMessage([{"type": "danger", "message": "Not able to create ODM project"}]) }
    });
}


$('form.admin-form').submit(function( event ) {
    // Prevent submit.
    // store form in separate constant
    const form = this;
    event.preventDefault();
    // register the currently chosen ODM project on our own database
    content_odm = {
        "odm_id": parseInt(document.getElementById("odm_config").value),
        "remote_id": parseInt(document.getElementById("odm_project").value)
    }
    content_odk = {
        "odk_id": parseInt(document.getElementById("odk_config").value),
        "remote_id": parseInt(document.getElementById("odk_project").value)
    }
    console.log(content);

    $.ajax({
        type: 'POST',
        url: `/api/odmproject/create_project`,
        data: JSON.stringify(content_odm),
        contentType: "application/json",
        dataType: 'json',
        // Submit parent form on success.
        success: function(data) {
            console.log(data);
            // place the newly created local odm project ref in the hidden odmproject_id
            document.getElementById("odmproject_id").value = data.id;
            // if odm worked, then also make an odk project
            $.ajax({
                type: 'POST',
                url: `/api/odkproject/create_project`,
                data: JSON.stringify(content_odk),
                contentType: "application/json",
                dataType: 'json',
                // Submit parent form on success.
                success: function(data) {
                    console.log(data);
                    document.getElementById("odkproject_id").value = data.id;
                    // both ODM and ODK projects are registered, now delete the parts in the form that are related to the odm and odk project selection
                    delete_groups = ["extra_config"]
                    delete_groups.forEach(e => $("#" + e).remove());
                    form.submit();
                },
                error: function() {
                    flashMessage([{"type": "danger", "message": "Not able to register ODK project locally"}])
                    $('button[type=submit], input[type=submit]').prop('disabled',false);
                }
            });
        },
        // Enable save button again.
        error: function() {
            flashMessage([{"type": "danger", "message": "Not able to register ODM project locally"}])
            $('button[type=submit], input[type=submit]').prop('disabled',false);
        }
    });
        // Prevent submit.

    // Prevent double actions.
//    $('button[type=submit], input[type=submit]').prop('disabled',true);
//    console.log("You have just clicked on --Save--")
//    const form = this;

});
