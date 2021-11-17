// use bathymetry_edit.js as example for form capture and submit after other stuff
function get_odk_projects()
{
    // get current id of odk server config
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
            if ("code" in data) {
                if (data.code == 401.2) {
                    flashMessage([{"type": "danger", "message": "ODK server authorization not accepted. Did you change username or password?"}]);
                } else {
                    // something else went wrong, report that!
                    flashMessage([{"type": "danger", "message": data.message}]);
                }
            } else {
                // populate the project dropdown with results
                data.forEach(function(x) {
                    var option = document.createElement("option");
                    option.text = x.name;
                    option.value = x.id;
                    project_select.add(option);
                });
                flashMessage([{"type": "success", "message": "ODK server found"}]);
            }
            document.getElementById("odk_project_create").disabled = false;
            document.getElementById("odk_project_delete").disabled = false;

        }
    )
    .fail(function() {
        // flash a message in case everything fails
        flashMessage([{"type": "danger", "message": "ODK server not available"}]);
    });
};


function get_odm_projects()
{
    // get current id odm server config
    const odmconfig_id = $('#odm_config').val();
    document.getElementById("odm_project_create").disabled = true;
    document.getElementById("odm_project_delete").disabled = true;
    // clear current projects in dropdown
    var project_select = document.getElementById("odm_project");
    removeOptions(project_select);
    addDisabledOption(project_select);
    $.ajax({
        url: `/api/odm/${odmconfig_id}/projects`,
        dataType: "json",
        success: function(data) {
            // populate the project dropdown with results
            console.log(data)
            data.forEach(function(x) {
                var option = document.createElement("option");
                option.text = x.name;
                option.value = x.id;
                project_select.add(option);
            });
            flashMessage([{"type": "success", "message": "ODM server found"}]);
            document.getElementById("odm_project_create").disabled = false;
            document.getElementById("odm_project_delete").disabled = false;
        },
        error: function(data) {
            console.log(data);
            if (data.status == 403) {
                flashMessage([{"type": "danger", "message": "ODM server authorization not accepted. Did you change username or password?"}]);
            } else if (data.status == 404) {
                flashMessage([{"type": "danger", "message": "ODM server not available"}]);
            } else {
                flashMessage([{"type": "danger", "message": `ODM Server responded with ${data.status} ${data.statusText}`}]);
            }
        }

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
//    forms = [`/static/forms/3DStreetView_main.xlsx`, `/static/forms/3DStreetView_fill.xlsx`];
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
            // add project to local database as reference
            content = {
                "odk_id": parseInt(odkconfig_id),
                "remote_id": parseInt(data.id)
            }
            $.ajax({
                type: 'POST',
                url: `/api/odkproject/create_project`,
                data: JSON.stringify(content),
                contentType: "application/json",
                dataType: 'json',
                // Submit parent form on success.
                function(odk_insert) {
                    console.log(odk_insert);
                }
            });
            // We're done, now refresh project list
            get_odk_projects();
            $('#newOdkProject').modal('hide');
            flashMessage([{"type": "success", "message": "New ODK project created"}]);
        },
        error: function() { flashMessage([{"type": "danger", "message": "Not able to create ODM project"}]) }
    });
}

$('form.admin-form').submit(function( event ) {
    // disable submit buttons, to prevent a user clicking twice
    flashMessage([{"type": "warning", "message": "Please wait while your mesh project is being generated..."}])
    $('button[type=submit], input[type=submit]').prop('disabled', true);
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
            $('button[type=submit], input[type=submit]').prop('disabled', false);
        }
    });
});

function delete_odk_project() {
    // switch off buttons to prevent submitting twice
    $("#odk_project_create").prop("disabled", true)
    $("#odk_project_delete").prop("disabled", true)
    id = parseInt(document.getElementById("odk_config").value)
    project_id = parseInt(document.getElementById("odk_project").value)
    if (confirm(`If you delete project then all forms, submissions and other data belonging to that ODK project will be permanently deleted`)) {
        url = `/api/odk/${id}/projects/${project_id}`
        $.ajax({
            type: 'DELETE',
            url: url,
            contentType: "application/json",
            dataType: 'json',
            // Submit parent form on success.
            success: function(data) {
                console.log(data);
                flashMessage([{"type": "success", "message": `Successfully deleted ODK project with id: ${project_id}`}])

                // place the newly created local odm project ref in the hidden odmproject_id
            },
            // Enable save button again.
            error: function() {
                flashMessage([{"type": "danger", "message": `Not able to delete ODK project with id: ${project_id}, did your permissions change?`}])
            }
        }).done(function() {
            // refresh list of ODK projects
            $("#odk_project").val('null').change()
            get_odk_projects();
            // switch buttons back on
            $("#odk_project_create").prop("disabled", false)
            $("#odk_project_delete").prop("disabled", false)
        });
    }
}


function delete_odm_project() {
    // switch off buttons to prevent submitting twice
    $("#odm_project_create").prop("disabled", true)
    $("#odm_project_delete").prop("disabled", true)
    id = parseInt(document.getElementById("odm_config").value)
    project_id = parseInt(document.getElementById("odm_project").value)
    if (confirm(`If you delete project then all tasks, photos, photogrammetry results and other data belonging to that ODM project will be permanently deleted`)) {
        url = `/api/odm/${id}/projects/${project_id}`
        $.ajax({
            type: 'DELETE',
            url: url,
            contentType: "application/json",
            dataType: 'json',
            // Submit parent form on success.
            success: function(data) {
                console.log(data);
                flashMessage([{"type": "success", "message": `Successfully deleted ODM project with id: ${project_id}`}])

                // place the newly created local odm project ref in the hidden odmproject_id
            },
            // Enable save button again.
            error: function(data) {
                console.log(data)
                flashMessage([{"type": "danger", "message": `Not able to delete ODM project with id: ${project_id}, did your permissions change?`}])
            }
        }).done(function() {
            // refresh list of ODK projects
            $("#odm_project").val('null').change()
            get_odm_projects();
            // switch buttons back on
            $("#odm_project_create").prop("disabled", false)
            $("#odm_project_delete").prop("disabled", false)
        });
    }
}

// map related jQuery
var map = new L.map('map').setView({lon: 0, lat: 0}, 2);
var maxAutoZoom = 15;
var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; <a href="https://openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors</a> ',
    tileSize: 256,
});
var googleSat = L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains:['mt0','mt1','mt2','mt3']
});
var googleTer = L.tileLayer('http://{s}.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains:['mt0','mt1','mt2','mt3']
});
var baseMaps = {
    "OpenStreetMap": osmLayer,
    "Google Satellite": googleSat,
    "Google Terrain": googleTer

}
L.control.layers(baseMaps).addTo(map);
osmLayer.addTo(map);
// add a scale at at your map.
var scale = L.control.scale().addTo(map);

// retrieve longitude and latitude form fields
pos_lng = document.getElementById('longitude');
pos_lat = document.getElementById('latitude');
// define change behaviour of form fields
pos_lat.onchange = function(){
    position = marker.getLatLng();
    changeMarker(pos_lat.value, position.lng);
};
pos_lng.onchange = function(){
    console.log("Changing longitude")
    position = marker.getLatLng();
    changeMarker(position.lat, pos_lng.value);
};

// Add a marker for the user to pick a location on the map
marker = new L.marker([pos_lng.value, pos_lat.value], {draggable: "true"});
// update the marker so that it sets everything in the same way
marker.addTo(map);

// change marker location by clicking (separate function)
map.on("click", function (e) {
    document.getElementById('latitude').value = e.latlng.lat;
    document.getElementById('longitude').value = e.latlng.lng;
    changeMarker(e.latlng.lat, e.latlng.lng);
});

// change marker location by dragging (both clicking and dragging is possible)
marker.on('dragend', function(e){
    var drag = e.target;
    var position = drag.getLatLng();
    console.log(position);
    changeMarker(position.lat, position.lng);
});

// set location of marker in map, as well as coordinates in form upon any change
function changeMarker(lat, lng){
    var newLatLng = new L.LatLng(lat, lng);
    marker.setLatLng(newLatLng, {draggable: "true"}).bindPopup(newLatLng).update();
    console.log("Setting new coordinates in form")
    document.getElementById('latitude').value = lat;
    document.getElementById('longitude').value = lng;
}
