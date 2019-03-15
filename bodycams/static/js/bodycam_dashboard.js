var stopVideo = function ( element ) {
    var iframe = element.querySelector( 'iframe');
    var video = element.querySelector( 'video' );
    if ( iframe ) {
        var iframeSrc = iframe.src;
        iframe.src = iframeSrc;
    }
    if ( video ) {
        video.pause();
    }
};
$(function() {
    $('.timeline-container').mousewheel(function(e, delta) {
        this.scrollLeft -= (delta * 40);
        e.preventDefault();
    });
    $(".timeline-container").scrollTo($("#timelineYear" + YEAR));
    $('#bodycam_details').on('hidden.bs.modal', function () {
        stopVideo(document.getElementById("bodycam_details"))
    })
    $('#shooting_details').on('hidden.bs.modal', function () {
        stopVideo(document.getElementById("shooting_details"))
    })
})
var vue_app = new Vue({
    	el: '#app',
        delimiters: ["((","))"],
        data: {
        	order: {
                title: 0,
                date: 0,
                description: 0,
                department: 0,
                state: 0,
                city: 0,
            },
        	city: "",
        	text: "",
			states_selected: [],
			departments_selected: [],
			races_selected: [],
			tags_selected: [],
			start_date: "",
			end_date: "",
        	races: RACES, // used for filling select2
            states: STATES, // used for filling select2
            departments: [],
            all_tags: ALL_TAGS, // used for filling select2
            bodycams: [],
            year: YEAR,
            displayed_video: "",
        	displayed_shooting: {}, // shooting to display in modal
        	displayed_bodycam: {
        		tags: [],
        	},
        },
        mounted: function() {
            var self = this;
            $.getJSON(BODYCAM_URLS["bodycam_data"], {"year": self.year}).done(function(data) {
                self.bodycams = data.bodycams[0]
                self.departments = data.departments
                $("#loader_cover").addClass("toggled");
                $("#body").removeAttr("style");
                $("#state_select").select2({
                    theme: "bootstrap",
                    placeholder: "Select state or states"
                })
                $('#state_select').on("change", function(e) { 
                    vue_app.states_selected = $(this).val();
                });
                $("#race_select").select2({
                    theme: "bootstrap",
                    placeholder: "Select race or races"
                })
                $('#race_select').on("change", function(e) { 
                    vue_app.races_selected = $(this).val();
                });
                $("#tag_select").select2({
                    theme: "bootstrap",
                    placeholder: "Select tag or tags"
                })
                $('#tag_select').on("change", function(e) { 
                    vue_app.tags_selected = $(this).val();
                });
                $("#department_select").select2({
                    theme: "bootstrap",
                    placeholder: "Select department or departments"
                })
                $('#department_select').on("change", function(e) { 
                    vue_app.departments_selected = $(this).val();
                });
                $('#start_date').datetimepicker({
                    format:"L",
                    useCurrent: false,
                });
                $('#end_date').datetimepicker({
                    format:"L",
                    useCurrent: false,
                });
                $('#start_date').on("change.datetimepicker", function (e) {
                    vue_app.start_date = $('#start_date').datetimepicker('viewDate');
                });
                $('#end_date').on("change.datetimepicker", function (e) {
                    vue_app.end_date = $('#end_date').datetimepicker('viewDate');
                });
            })
        },
        methods: {
        	displayAge: function(age) {
				/*Handles displaying age to avoid displaying -1

				Arguments:
				:param age: integer from -1 - positive infinity

				Returns:
				If age < 0, returns "No Age"
				else returns age
				*/
                if (age > -1) {
                    return age
                }
                else {
                    return "No Age"
                }
            },
            openBodycamDetails: function(id) {
				/* Displays a bodycam's details attached to the bodycam in a modal.

				Arguments:
				:param id: integer from 1 - positive infinity

				Searches for the bodycam that has an id matching the param id, selects that bodycam as
				the displayed_bodycam which gets automatically populated in the modal via 2-way binding
				then opens the modal

				Returns:
				Nothing
				*/
                bodycam = this.bodycams.find(function(bodycam) {
                    return bodycam.id == id
                })
                this.displayed_bodycam = bodycam
                $('#bodycam_details').modal('toggle');
            },
        	openDetails: function(obj) {
				/*Displays a shooting for a bodycam.

				Arguments:
				:param obj: a shooting as JSON object

				Sets the displayed_shooting to the object passed, which gets automatically populated in the modal
				via 2-way binding then opens the modal

				Returns:
				Nothing
				*/
                this.displayed_shooting = obj;
                $('#shooting_details').modal('toggle');
            },
            editBodycam: function(id) {
				/*Chooses the bodycam to be edited and passes the data to the nav_app

				The nav_app is in charge of all editing, so we just need to pass the data to the nav_app.
				We start by iterating through the bodycams until we find the one who's id matches the argument
				passed.

				We then begin populating an array with the tags since passing the tags directly for some reason
				results in null (suspect it has something to do with variable lifespan and javascript passing by reference
				and not by value for object as opposed to basic valuesbut this solves the problem so
				not worth checking). TWe then assign the nav_app bodycam to match the details of the current bodycam
				and set the creating flag to false, which means the nav_app will submit the details to the edit endpoint
				instead of the creation endpoint.

				We then call the openBodycamModal function of nav_app, which will populate the modal's non-2-way-bound
				form fields with jQuery and open the editing modal.

				Arguments:
				:param id: an integer id

				Returns:
				Nothing
				*/
                for (var x = 0; x < this.bodycams.length; x++) {
                    if (this.bodycams[x].id == id) {
                        tags = []
                        for (var y = 0; y < this.bodycams[x].tags.length; y++) {
                            tags.push(this.bodycams[x].tags[y].text)
                        }
                        nav_app.bodycam.id = this.bodycams[x].id
	                    nav_app.bodycam.title = this.bodycams[x].title
	                    nav_app.bodycam.video = this.bodycams[x].video
	                    nav_app.bodycam.description = this.bodycams[x].description
	                    nav_app.bodycam.department = this.bodycams[x].department
	                    nav_app.bodycam.state = this.bodycams[x].state_value
	                    nav_app.bodycam.city = this.bodycams[x].city
	                    nav_app.bodycam.date = this.bodycams[x].date
	                    nav_app.bodycam.tags = tags
	                    if (this.bodycams[x].shooting) {
	                    	nav_app.bodycam.shooting = "" + this.bodycams[x].shooting.id;
	                    }
                        nav_app.creating = false;
                        nav_app.openBodycamModal();
                        return;
                    }
                }
        	},
            deleteBodycam: function(id) {
				/*Confirms user's decision then deletes a bodycam

				We confirm that they want to delete the bodycam, and on confirmation, send a
				AJAX POST request to the delete endpoint, with a dictionary including the
				csrfmiddlewaretoken and the pk. On success we then reload the page, on failure, we display an error

				Arguments:
				:param id: an integer id of a bodycam to be deleted

				Returns:
				Nothing
				*/
                var data = {
                    "pk": parseInt(id),
                    "csrfmiddlewaretoken": CSRFMIDDLEWARETOKEN,
                }
                $.confirm({
                    type: "red",
                    title: "Are you sure?",
                    content: "This action cannot be undone. Are you sure you want to continue?",
                    buttons: {
                        Yes: function() {
                            $.ajax({
                                type: "POST",
                                url: BODYCAM_URLS["dashboard"],
                                data: data,
                                success: function() {
                                    $.alert({
                                        title: 'Success!',
                                        content: 'Bodycam deleted succesfully. The page will now reload.',
                                        type: 'green',
                                        typeAnimated: true,
                                        autoClose: 'close|4000',
                                        buttons: {
                                            close: function () {
                                                window.location.reload()
                                            }
                                        }
                                    });
                                },
                                error: function(data) {
                                    console.log(data)
                                    $.confirm({
                                        title: 'Encountered an error!',
                                        content: 'Something went wrong when processing the request. Send Pedro a text message and save this information: ' + data.responseText,
                                        type: 'red',
                                        typeAnimated: true,
                                        backgroundDismiss: false,
                                        buttons: {
                                            close: function () {
                                            }
                                        }
                                    });
                                },
                            });
                        },
                        Cancel: function() {

                        }
                    }
                })
            },
        	resetFilters: function() {
				/*Resets the filter choices

				Sets 2-way-bound variables to their default values, and uses jQuery to reset non-2-way-bound variables

				Arguments:
				None

				Returns:
				None
				*/
                var self = this;
                $("#state_select").val([]).trigger("change")
                $("#race_select").val([]).trigger("change")
                $("#tag_select").val([]).trigger("change")
                $("#department_select").val([]).trigger("change");
                self.text = "";
                self.city = "";
                self.states_selected = [];
                self.departments_selected = [];
                self.races_selected = [];
                self.tags_selected = [];
                self.start_date = "";
                self.end_date = "";
                $('#start_date').datetimepicker('clear');
                $('#end_date').datetimepicker('clear');
            },
            calculateNextYear: function() {
				/*Calculates the next year for setting the url of the Next Year button

				Uses the year passed from the server (which is the year currently being viewed) to
				decide which year is next

				Arguments:
				None

				Returns:
				None
				*/
                var year = moment(YEAR, "YYYY").add(1, "y").format("YYYY")
                var url = BODYCAM_URLS["dashboard_date"];
                url = url.replace("1234", year);
                return url;
            },
            calculatePreviousYear: function() {
				/*Calculates the previous year for setting the url of the Previous Year button

				Uses the year passed from the server (which is the year currently being viewed) to
				decide which year is past

				Arguments:
				None

				Returns:
				None
				*/
                var year = moment(YEAR, "YYYY").subtract(1, "y").format("YYYY")  
                var url = BODYCAM_URLS["dashboard_date"];
                url = url.replace("1234", year);
                return url;
            },
            order_by: function(attribute) {
				/*Sets the order object that is used in the computed function for displaying bodycams

				Given the attribute, we set that attribute to 1 if it is -1 or 0, or -1 if it is set to 1,
				and sets all other attributes to 0.

				Arguments:
				:param attribute: a string of a key
				*/
                var self = this;
                this.order_attribute = attribute;
                $.each(self.order, function(key, value) {
                    if (key == attribute) {
                        if (self.order[attribute] == 0) {
                            self.order[attribute] = 1;
                        }
                        else if (self.order[attribute] == 1) {
                            self.order[attribute] = -1;
                        }
                        else {
                            self.order[attribute] = 1;
                        }
                    }
                    else {
                        self.order[key] = 0;
                    }
                });
            },
        },
        computed: {
        	currentYear: function() {
				/*Selects the current year

				This is used for deciding whether to display the "Next Year" button, which shouldn't be displayed for
				accessing a future years

				Arguments:
				None

				Returns:
				current year as "YYYY"

				*/
                return moment().format("YYYY")
            },
        	displayed_bodycams: function() {
				/*Calculates what bodycams should be displayed to the user and returns bodycams
				
				Copies the list of bodycams (so we don't affect the list)
				Filters by text, then city, then states, then departments, then races of the shooting,
				then tags, then start date, then end date
				*/
                var self = this;
                var displayed_bodycams = this.bodycams.slice();
                if (this.text.length > 0) {
                    displayed_bodycams = displayed_bodycams.filter(function(bodycam) {
                        if (bodycam.title.toUpperCase().indexOf(self.text.toUpperCase()) > -1) {
                            return true;
                        }
                        else if (bodycam.description.toUpperCase().indexOf(self.text.toUpperCase()) > -1) {
                            return true;
                        } 
                    })
                }
                if (this.city.length > 0) {
                    displayed_bodycams = displayed_bodycams.filter(function(bodycam) {
                        if (bodycam.city.toUpperCase().indexOf(self.city.toUpperCase()) > -1) {
                            return true;
                        } 
                    })
                }
                if (this.states_selected.length > 0) {
                    displayed_bodycams = displayed_bodycams.filter(function(bodycam) {
                        if (self.states_selected.indexOf("" + bodycam.state_value) > -1) {
                            return true;
                        }
                    })
                }
                if (this.departments_selected.length > 0) {
                    displayed_bodycams = displayed_bodycams.filter(function(bodycam) {
                        if (self.departments_selected.indexOf(bodycam.department) > -1) {
                            return true;
                        }
                    })
                }
                if (this.races_selected.length > 0) {
                    displayed_bodycams = displayed_bodycams.filter(function(bodycam) {
                    	if (typeof bodycam.shooting == "undefined") {
                    		return false;
                    	}
                        if (self.races_selected.indexOf("" + bodycam.shooting.race_value) > -1) {
                            return true;
                        }
                    })
                }
                if (this.tags_selected.length > 0) {
                    displayed_bodycams = displayed_bodycams.filter(function(bodycam) {
                        for (var y = 0; y < bodycam.tags.length; y++) {
                            if (self.tags_selected.indexOf(bodycam.tags[y].text) > -1) {
                                return true;
                            }
                        }
                    })
                }
                if (this.start_date.length != 0) {
                    displayed_bodycams = displayed_bodycams.filter(function(bodycam) {
                        var date = moment(bodycam.date, "YYYY-MM-DD");
                        if (self.start_date < date) {
                            return true;
                        }
                    })
                }
                if (this.end_date.length != 0) {
                    displayed_bodycams = displayed_bodycams.filter(function(bodycam) {
                        var date = moment(bodycam.date, "YYYY-MM-DD");
                        if (self.end_date > date) {
                            return true;
                        }
                    })
                }
                return displayed_bodycams
            }
        }
	})