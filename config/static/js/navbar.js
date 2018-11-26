$(function() {
            // this initializes all DOM elements that rely on JS init, and creates
            // event listeners to maintain Vue binding
            $('#bodycam_new_date').datetimepicker({
                format:"L",
                useCurrent: false,
            });
            $('#bodycam_new_date').on("change.datetimepicker", function (e) {
                nav_app.bodycam.date = $('#bodycam_new_date').datetimepicker('viewDate');
            });
            $("#select_shooting_for_bodycam").select2({
                theme: "bootstrap",
                placeholder: "Select shooting",
                dropdownParent: $("#add_bodycam"),
                minimumInputLength: 3,
                ajax: {
                    url: URLS["ajax_shooting"],
                    dataType: 'json',
                  }
            })
            $('#select_shooting_for_bodycam').on("change", function(e) { 
                if ($(this).val() != "") {
                    // if the user selects a shooting, then the duel submit
                    // isn't allowed.
                    $("#bodycam_shooting_duo").prop("disabled", true)
                }
                else {
                    $("#bodycam_shooting_duo").prop("disabled", false)   
                }
                nav_app.bodycam.shooting = $(this).val();
            });
            
            $("#new_bodycam_state_select").select2({
                theme: "bootstrap",
                placeholder: "Select state",
                dropdownParent: $("#add_bodycam"),
            })
            $('#new_bodycam_state_select').on("change", function(e) { 
                nav_app.bodycam.state = $(this).val();
            });
            $("#new_bodycam_tags_select").select2({
                theme: "bootstrap",
                tags: true,
                placeholder: "Select tags"
            });
            $('#new_bodycam_tags_select').on("change", function(e) { 
                nav_app.bodycam.tags = $(this).val();
            });
            $('#new_date').datetimepicker({
                format:"L",
                useCurrent: false,
            });
            $('#new_date').on("change.datetimepicker", function (e) {
                nav_app.shooting.date = $('#new_date').datetimepicker('viewDate');
            });
            $("#new_state_select").select2({
                theme: "bootstrap",
                placeholder: "Select state",
                dropdownParent: $("#add_killing"),
            })
            $('#new_state_select').on("change", function(e) { 
                nav_app.shooting.state = $(this).val();
            });
            
            $("#new_race_select").select2({
                theme: "bootstrap",
                dropdownParent: $("#add_killing"),
                placeholder: "Select race"
            })
            $("#new_tags_select").select2({
                theme: "bootstrap",
                tags: true,
                placeholder: "Select tags"
            });
            $('#new_tags_select').on("change", function(e) { 
                nav_app.shooting.tags = $(this).val();
            });
            $('#new_race_select').on("change", function(e) { 
                nav_app.shooting.race = $(this).val();
            });
            $("#new_gender_select").select2({
                theme: "bootstrap",
                placeholder: "Select gender"
            })
            $('#new_gender_select').on("change", function(e) { 
                nav_app.shooting.gender = $(this).val();
            });
        })
        var nav_app = new Vue({
            el: '#nav_related',
            delimiters: ["((","))"],
            data: {
                // if this is false, then the data is prepopulated and we post to edit instead of new, set DOM title to "edit"
                creating: true, 
                // we use this to decide whether we need to refresh the page on
                // successful submission (since we need to subvmit first a bodycam, then a shooting)
                submitting_duel: false, 
                // if this is false, then the data is prepopulated and we post to edit instead of new, set DOM title to "edit"

                creating_bodycam: true,
                // we use these two to link the two together prior to refreshing
                bodycam_id: "",
                shooting_id: "",
                // two way binding for adding new tags to dropdown
                tag_input: "",
                // two way binding for adding new tags to dropdown
                bodycam_tag_input: "",
                bodycam: {
                    id: "",
                    title: "",
                    video: "",
                    description: "",
                    department: "",
                    state: "",
                    city: "",
                    date: "",
                    tags: [],
                    shooting: "",
                },
                shooting: {
                    id: "",
                    name: "",
                    date: "",
                    race: "",
                    age: "",
                    gender: "",
                    state: "",
                    city: "",
                    video_url: "",
                    sources: [],
                    description: "",
                    tags: [
                    ]
                },
                genders: GENDERS, // used for filling select2
                all_tags: ALL_TAGS, // used for filling select2
            },
            methods: {
                clearBodycamModal: function() {
                    /*Closes the bodycam creation/edit modal and resets the data in the 2 way binding to a blank slate
                    
                    Arguments:
                    None
                    
                    Returns:
                    None
                    */
                    this.bodycam_id = ""
                    this.shooting_id = ""
                    this.bodycam.id = ""
                    this.bodycam.title = ""
                    this.bodycam.video = ""
                    this.bodycam.description = ""
                    this.bodycam.department = ""
                    this.bodycam.state = ""
                    this.bodycam.city = ""
                    this.bodycam.date = ""
                    this.bodycam.tags = []
                    this.bodycam.shooting = ""
                    this.creating = true
                    this.submitting_duel = false
                    this.bodycam_tag_input = ""
                    $("#select_shooting_for_bodycam").val([]).trigger("change")
                    $("#new_bodycam_state_select").val([]).trigger("change");
                    $("#new_bodycam_tags_select").val([]).trigger("change");
                    $('#bodycam_new_date').datetimepicker('clear');
                },
                clearModal: function() {
                    /*Closes the shooting creation/edit modal and resets the data in the 2 way binding to a blank slate
                    
                    If we are submitting a bodycam and shooting in tandem, we check to see whether they actually did intend to close the modal
                    since they will no longer be able to link them automatically and will have to do so manually.
                    
                    If they confirm, or if they aren't submitting a tandem entry, then we reset the data and close the modal
                    
                    Arguments:
                    None
                    
                    Returns:
                    None
                    */
                    var cont = false;
                    if (this.submitting_duel) {
                        // lets make sure that they want to do this before we close since this will stop a shooting from being
                        // linked to the previously submitted bodycam
                        $.confirm({
                            title: 'Are you sure you want to do this?',
                            content: "You'll have to manually connect the bodycam we just made to a new one later if you stop now. Are you sure you want to continue?",
                            type: 'purple',
                            typeAnimated: true,
                            buttons: {
                                Yes: function(){
                                    cont = true;
                                },
                                No: function () {

                                }
                            }
                        });
                    }
                    else {
                        cont = true;   
                    }
                    if (!cont) {
                        return;
                    }
                    this.tag_input = ""
                    this.bodycam_id = ""
                    this.shooting_id = ""
                    this.creating = true
                    this.submitting_duel = false
                    this.tag_input = ""
                    this.shooting.id = ""
                    this.shooting.name = ""
                    this.shooting.date = ""
                    this.shooting.race = ""
                    this.shooting.age = ""
                    this.shooting.gender = ""
                    this.shooting.state = ""
                    this.shooting.city = ""
                    this.shooting.video_url = ""
                    this.shooting.sources = []
                    this.shooting.description = ""
                    this.shooting.tags = []
                    $("#new_state_select").val([]).trigger("change")
                    $("#new_race_select").val([]).trigger("change")
                    $("#new_tags_select").val([]).trigger("change")
                    $("#new_gender_select").val([]).trigger("change");
                    $('#new_date').datetimepicker('clear');
                },
                submitBodycamWithShooting: function() {
                    /*Sets the tandem submit flag to true so that the following submissions perform the appropriate linking AJAX calls
                    
                    Arguments:
                    None
                    
                    Returns:
                    None
                    */
                    this.submitting_duel = true
                    this.submitBodycam();
                },
                submitBodycam: function() {
                    /*Submits a bodycam.
                    
                    First does front end sanity checks for UX, then submits the data to the creation endpoint if creating is true
                    otherwise submits to the editing endpoint.
                    
                    If the submitting_duel flag is true, then it saves the returned bodycam_id, and prompts the user to
                    create a shooting now to link to the submitted bodycam. Otherwise it refreshes the page.
                    
                    Arguments:
                    None
                    
                    Returns:
                    None
                    */
                    var self = this;
                    // check data before submitting
                    if (self.bodycam.title.length == 0) {
                        showErrorMessage("Please review your submission", "The title cannot be blank.");
                        return;
                    }
                    if (self.bodycam.video.length == 0) {
                        showErrorMessage("Please review your submission", "The video cannot be blank.");
                        return;
                    }
                    if (self.bodycam.state.length == 0) {
                        showErrorMessage("Please review your submission", "The state cannot be blank.");
                        return;
                    }
                    if (self.bodycam.date == "") {
                        showErrorMessage('Please review your submission', "Date cannot be blank.")
                        return;
                    }
                    data = {
                        csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
                        bodycam: JSON.stringify(self.bodycam)
                    }
                    date = self.bodycam.date.format("YYYY-MM-DD")
                    data.bodycam.date = date;
                    
                    if (self.creating) {
                        // we are creating a new bodycam, so we post to bodycam creation
                        // then we either refresh or prompt the user to create a shooting
                        $.ajax({
                            type: "POST",
                            url: URLS["bodycam_create"],
                            data: data,
                            success: function(data) {
                                if (self.submitting_duel) {
                                    showSuccessMessage("Bodycam submitted. Let's create the shooting now.", false)
                                    self.clearBodycamModal()
                                    self.bodycam_id = data; // gets reset in clearBodycamModal
                                    self.submitting_duel = true; // gets reset in clearBodycamModal
                                    $("#add_bodycam").modal("toggle")
                                    $("#add_killing").modal("toggle")
                                }
                                else {
                                    showSuccessMessage('Bodycam submitted. The page will now reload.', true)
                                }
                            },
                            error: function(data) {
                                if (data.status == 400) {
                                    showErrorMessage('Please review your submission', data.responseText)
                                }
                                else if (data.status == 406) {
                                    $.confirm({
                                        title: 'Something went wrong.',
                                        content: data.responseText,
                                        type: 'red',
                                        typeAnimated: true,
                                        backgroundDismiss: false,
                                        buttons: {
                                            "Print Error": function() {
                                                var mywindow = window.open('', 'PRINT', 'height=400,width=600');

                                                mywindow.document.write('<html><head><title>' + document.title  + '</title>');
                                                mywindow.document.write('</head><body >');
                                                mywindow.document.write('<h1>' + document.title  + '</h1>');
                                                mywindow.document.write($(".jconfirm-content")[0].innerHTML);
                                                mywindow.document.write('</body></html>');

                                                mywindow.document.close(); // necessary for IE >= 10
                                                mywindow.focus(); // necessary for IE >= 10*/

                                                mywindow.print();
                                                mywindow.close();

                                                return true;
                                            },
                                            close: function () {
                                                window.location.reload(true)
                                            }
                                        }
                                    });
                                }
                                else {
                                    showErrorMessage('Encountered an error!', 'Something went wrong when processing the request. Send Pedro a text message and save this information: ' + data.responseText)
                                }
                            },
                        });
                    }
                    else {
                        $.ajax({
                            type: "POST",
                            url: URLS["bodycam_edit"],
                            data: data,
                            success: function() {
                                showSuccessMessage('Bodycam edited succesfully. The page will now reload.', true)
                            },
                            error: function(data) {
                                if (data.status == 400) {
                                    showErrorMessage('Please review your submission', data.responseText)
                                }
                                else {
                                    showErrorMessage('Encountered an error!', 'Something went wrong when processing the request. Send Pedro a text message and save this information: ' + data.responseText)
                                }
                            },
                        });
                    }
                },
                unlinkShooting: function() {
                    /*Removes the shooting from the bodycam
                    
                    There is no way for the user to remove a shooting without adding a new one without this method
                    
                    Arguments:
                    None
                    
                    Returns:
                    None
                    */
                    var self = this;
                    self.bodycam.shooting = -1;
                    showSuccessMessage("Shooting has been unlinked. If you want to relink it, refresh the page without submitting the changes.", false)
                },
                submitKilling: function() {
                    /*Submits a shooting
                    
                    First does front end sanity checks for UX, then submits the data to the creation endpoint if creating is true
                    otherwise submits to the editing endpoint.
                    
                    If the submitting_duel flag is true, then it saves the returned shooting_id, and sends another AJAX call to the
                    linking endpoint with the two ids to be linked. On success, it alerts the user and refreshes the page. Otherwise
                    displays an error
                    
                    Arguments:
                    None
                    
                    Returns:
                    None
                    */
                    var self = this;
                    // the video has to be in the proper youtube format
                    if (self.shooting.video_url.length > 0 && self.shooting.video_url.search(/http[s]*:\/\/www\.youtube\.com\/watch\?v=/) < 0) {
                        showErrorMessage('Please review your submission', "The video URL must be a valid, unshortened Youtube URL.")
                        return;
                    }
                    else if (self.shooting.video_url.length > 0 && self.shooting.video_url.search(/http[s]*:\/\/www\.youtube\.com\/watch\?v=/) > -1) {
                        // lets strip away url params
                        if (self.shooting.video_url.indexOf("&") > -1) {
                            self.shooting.video_url = self.shooting.video_url.substring(0, self.shooting.video_url.indexOf("&"));
                        }
                    }
                    // check data
                    if (self.shooting.date == "") {
                        showErrorMessage('Please review your submission', "Date cannot be blank.")
                        return;
                    }
                    if (self.shooting.state == "") {
                        showErrorMessage('Please review your submission', "State cannot be blank.")
                        return;
                    }
                    if (self.shooting.race == "") {
                        showErrorMessage('Please review your submission', "Race cannot be blank.")
                        return;
                    }
                    if (self.shooting.gender == "") {
                        showErrorMessage('Please review your submission', "Gender cannot be blank.")
                        return;
                    }
                    data = {
                        csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
                        shooting: JSON.stringify(self.shooting)
                    }
                    if (self.creating) {
                        $.ajax({
                            type: "POST",
                            url: URLS["shooting_create"],
                            data: data,
                            success: function(data) {
                                if (self.submitting_duel) {
                                    self.shooting_id = data
                                    // time to link the two together
                                    $.ajax({
                                        type: "POST",
                                        url: URLS["link_shooting_bodycam"],
                                        data: {
                                            csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
                                            bodycam_id:  parseInt(self.bodycam_id),
                                            shooting_id: parseInt(self.shooting_id),
                                        },
                                        success: function() {
                                            showSuccessMessage('Killing and bodycam submitted and linked. The page will now reload.', true)
                                        },
                                        error: function() {
                                            showErrorMessage("Encountered an error!", "Something went wrong linking the killing and bodycam, but we've created both of them. Send Pedro a text and tell him to link: bodycam " + self.bodycam_id + " and killing " + self.shooting_id +", and that the error that caused this was: " + data)
                                        }
                                    })
                                }
                                else {
                                    showSuccessMessage('Killing submitted. The page will now reload.', true)
                                }
                            },
                            error: function(data) {
                                if (data.status == 400) {
                                    showErrorMessage('Please review your submission', data.responseText)
                                }
                                else {
                                    showErrorMessage('Encountered an error!', 'Something went wrong when processing the request. Send Pedro a text message and save this information: ' + data.responseText)
                                }
                            },
                        });
                    }
                    else {
                        $.ajax({
                            type: "POST",
                            url: URLS["shooting_edit"],
                            data: data,
                            success: function() {
                                showSuccessMessage('Killing edited succesfully. The page will now reload.', !self.submitting_duel)
                            },
                            error: function(data) {
                                if (data.status == 400) {
                                    showErrorMessage('Please review your submission', data.responseText)
                                }
                                else {
                                    showErrorMessage('Encountered an error!', 'Something went wrong when processing the request. Send Pedro a text message and save this information: ' + data.responseText)
                                }
                            },
                        });
                    }
                },
                spliceSource: function(index) {
                    /*Removes a source from the shooting creation modal list.
                    
                    This is used if the user wants to remove a source that isn't the last source added.
                    
                    Arguments:
                    :param index: the index of the source to be removed
                    
                    Returns:
                    None
                    */
                    this.shooting.sources.splice(index, 1);
                },
                removeSource: function() {
                    /*Removes the last created source from the shooting creation modal list. 
                    
                    Arguments:
                    None
                    
                    Returns:
                    None
                    */
                    // removes the most recently added source from the killing
                    this.shooting.sources.pop()
                },
                addSource: function() {
                    /*Adds a new shooting input to the list
                    
                    Since the 2 way binding shows an input for each source added, and automatically sets up
                    the 2 way binding from the input to the array element in the shooting.sources array, all
                    we need to do here is add another empty element and allow them to type whatever they want.
                    
                    Arguments:
                    None
                    
                    Returns:
                    None
                    */
                    this.shooting.sources.push("")
                },
                resetShootingSelection: function() {
                    /*Resets the Shooting selection Select2 for linking a new bodycam to an existing shooting
                    
                    Select2 won't allow the user to reselect the empty value, so we provide this. If we didnt'
                    then they wouldn't be able to change their mind and submit a new shooting, which means they'd have to
                    exit out of the modal entirely
                    
                    Arguments:
                    None
                    
                    Returns:
                    None
                    */
                    // in case the user decides he actually wants to add a new killing to this bodycam
                    var self = this;
                    self.bodycam.shooting = "";
                    $("#select_shooting_for_bodycam").val(self.bodycam.shooting).trigger("change");
                    $("#bodycam_shooting_duo").prop("disabled", false)   
                },
                openBodycamModal: function() {
                    /*Initializes the creation/editing modal for bodycams
                    
                    The data to be populated comes from the vue_app running on the page, which passes the data to the nav_app.
                    
                    Arguments:
                    None
                    
                    Returns:
                    None
                    */
                    var self = this;
                    var shooting = self.bodycam.shooting;
                    $("#add_bodycam").modal("toggle")
                    if (!self.creating ) {
                        $("#bodycam_new_date").datetimepicker("date", moment(self.bodycam.date, "YYYY-MM-DD"))
                        $("#new_bodycam_state_select").val(self.bodycam.state).trigger("change")
                        $("#new_bodycam_tags_select").val(self.bodycam.tags).trigger("change")
                        $("#select_shooting_for_bodycam").val(shooting).trigger("change")
                    }
                    $("#defaultSubmit").prop("disabled", false)
                },
                openKillingModal: function() {
                    /*Initializes the creation/editing modal for shootings
                    
                    The data to be populated comes from the vue_app running on the page, which passes the data to the nav_app.
                    
                    Arguments:
                    None
                    
                    Returns:
                    None
                    */
                    var self = this;
                    $("#add_killing").modal("toggle")
                    if (!self.creating ) {
                        $("#new_date").datetimepicker("date", moment(self.shooting.date, "YYYY-MM-DD"))
                        $("#new_state_select").val(self.shooting.state).trigger("change")
                        $("#new_race_select").val(self.shooting.race).trigger("change")
                        $("#new_tags_select").val(self.shooting.tags).trigger("change")
                        $("#new_gender_select").val(self.shooting.gender).trigger("change");

                    }
                }
            }
        });