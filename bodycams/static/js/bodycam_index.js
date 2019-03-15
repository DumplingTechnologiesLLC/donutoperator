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
    $('#bodycam_details').on('hidden.bs.modal', function () {
        stopVideo(document.getElementById("bodycam_video"))
    })
    $('#shooting_details').on('hidden.bs.modal', function () {
        stopVideo(document.getElementById("bodycam_video"))
    })
    $('.timeline-container').mousewheel(function(e, delta) {
        this.scrollLeft -= (delta * 40);
        e.preventDefault();
    });
    $(".timeline-container").scrollTo($("#timelineYear" + YEAR));
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
    $('#video_modal').on('hidden.bs.modal', function () {
            // do something…
        vue_app.closeVideoModal();
    })
})
    var vue_app = new Vue({
    	el: '#app',
        delimiters: ["((","))"],
        data: {
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
            displayed_bodycam: {},
        	displayed_shooting: {},
            expanded_bodycams: [], // used for tracking which bodycams were expanded to update text of buttons
        },
        mounted: function() {
            var self = this;
            $.getJSON(BODYCAM_URLS["bodycam_data"], {"year": self.year}).done(function(data) {
                self.bodycams = data.bodycams[0]
                self.departments = data.departments
                $("#loader_cover").addClass("toggled");
                $("#body").removeAttr("style");
                $("#department_select").select2({
                    theme: "bootstrap",
                    placeholder: "Select department or departments"
                })
                $('#department_select').on("change", function(e) { 
                    vue_app.departments_selected = $(this).val();
                });
            })

        },
        methods: {
            generateThumbnail: function(iframeCode) {
                /* Generates a thumbnail based on HTML for an iframe

                Arguments:
                :param iframeCode: the iframe code necessary to generate the thumbnail

                Returns:
                the data url for the image
                */
                var $my_div = $('<div/>').html(iframeCode).contents()[0];  // $($.parseHTML(iframeCode));
                var image = "";
                var iframe_src = $($my_div).attr('src');
                try {
                    var youtube_video_id = iframe_src.match(/youtube\.com.*(\?v=|\/embed\/)(.{11})/).pop();
                    if (youtube_video_id.length == 11) {
                        return '<img style="cursor: pointer; width:100%; height:100%" src="//img.youtube.com/vi/'+youtube_video_id+'/0.jpg">';
                    }
                    else {
                        return '<div style="cursor: pointer; background-color:gray; width:100%; height:183px" class="d-flex flex-row p-2 flex-column justify-content-center text-center flex-fill">' +
                            '<div class="align-self-center p-2"><h5 style="color:white;">No Automatic Thumbnail Available</h5></div>' +
                        '</div>'
                        // return '<img style="cursor: pointer; width:100%; height:183px" src="//img.youtube.com/vi/0/0.jpg">';  
                    }
                } catch(error) {
                    return '<div style="cursor: pointer; background-color:gray; width:100%; height:183px" class="d-flex flex-row p-2 flex-column justify-content-center text-center flex-fill">' +
                            '<div class="align-self-center p-2"><h5 style="color:white;">No Automatic Thumbnail Available</h5></div>' +
                        '</div>'
                    // return '<img style="cursor: pointer; width:100%; height:100%" src="//img.youtube.com/vi/0/0.jpg">';  
                }
            },
            bodycamDescription: function(id) {
                /*Returns a class object of CSS classes to be applied.
                This is what actually toggles the expanded or collapsed text.

                Arguments:
                :param id: the id of a bodycam. Used to check whether it exists in the
                expanded_bodycams array

                Returns:
                a json array of CSS classes with boolean flag on whether to apply or not
                */
                var self = this;
                return {
                    "content": true, // this is always applied
                    "bodycam-description": true, // this is always applied
                    'collapsed-description': self.expanded_bodycams.indexOf(id) < 0
                }
            },
            toggleText: function(id) {
                /*This sets the "expand" button text to expand or collapse based on whether
                the particular description is expanded or not.
                
                Arguments:
                :param id: the id of a bodycam. will be checked in the array of opened
                bodycams to decide whether to set text to expand or collapse.
                If it exists in the array, will be set to collapse

                Returns:
                Collapse if the id exists in the array
                Expand otherwise
                */
                var self = this;
                if (self.expanded_bodycams.indexOf(id) > -1) {
                    // already expanded. Time to contract
                    return "Collapse"
                }
                else {
                    // contracted. Please expand
                    return "Expand"
                }
            },
            toggleDescription: function(id) {
                /*Adds or removes an id from the expanded_bodycams array, which in turn
                triggers the classes to change via 2-way binding.

                Arguments:
                :param id: the id of a bodycam

                Returns:
                Nothing
                */
                var self = this;
                if (self.expanded_bodycams.indexOf(id) > -1) {
                    // already expanded. Time to contract
                    self.expanded_bodycams.splice(self.expanded_bodycams.indexOf(id), 1);
                }
                else {
                    // contracted. Time to expand
                    self.expanded_bodycams.push(id);
                }
            },
            lengthCheck: function(bodycam) {
                /*Is used to decide whether we need to truncate the description

                Arguments:
                :param bodycam: a bodycam JSON object

                Returns:
                true if the description length is greater than 266
                false otherwise
                */
                return bodycam.description.length > 266
            },
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
            closeVideoModal: function() {
                /*Sets the displayed_bodycam to an empty object when the modal closes

                This is necessary because otherwise the video continues to play after
                the modal closes. We need to remove the video from the DOM.

                Arguments:
                None

                Returns:
                None
                */
                this.displayed_bodycam = {}
            },
            showVideo: function(id) {
                /*Displays a bodycams video. This was changed from displaying all videos
                to save on bandwidth and save a user's data if on mobile.

                Sets the displayed_bodycam to the bodycam who's id matches the id passed,
                which gets automatically populated in the modal via 2 way binding, then opens
                the modal

                Arguments:
                :param id: a pk of a bodycam

                Returns:
                None
                */
                bodycam = this.bodycams.find(function(bodycam) {
                    return bodycam.id == id
                })
                this.displayed_bodycam = bodycam;
                $("#video_modal").modal("toggle");
            },
        	openDetails: function(id) {
				/*Displays a shooting for a bodycam.

				Arguments:
				:param id: a pk of a bodycam

				Sets the displayed_shooting to the shooting of the bodycam who's id matches the
                argument  passed, which gets automatically populated in the modal
				via 2-way binding then opens the modal

				Returns:
				Nothing
				*/
                bodycam = this.bodycams.find(function(bodycam) {
                    return bodycam.id == id
                })
                this.displayed_shooting = bodycam.shooting
                $('#shooting_details').modal('toggle');
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
                this.text = "";
                this.city = "";
                this.states_selected = [];
                this.departments_selected = [];
                this.races_selected = [];
                this.tags_selected = [];
                this.start_date = "";
                this.end_date = "";
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
                var url = BODYCAM_URLS["date_index"];
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
                var url = BODYCAM_URLS["date_index"];
                url = url.replace("1234", year);
                return url;
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