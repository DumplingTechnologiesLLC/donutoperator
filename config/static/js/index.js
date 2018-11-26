$(function() {
    setTimeout(function() {
        // loader is on base.html. Blocks the user from doing anything until page loads
        $("#loader_cover").addClass("toggled");
        $("#body").removeAttr("style")
    },2000);
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
    $("#gender_select").select2({
        theme: "bootstrap",
        placeholder: "Select gender or genders"
    })
    $('#gender_select').on("change", function(e) { 
        vue_app.genders_selected = $(this).val();
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
var vue_app = new Vue({
    el: '#app',
    delimiters: ["((","))"],
    data: {
        order: {
            name: 0,
            age: 0,
            date: 0,
            race: 0,
            gender: 0,
            state: 0,
            city: 0,
        },
        order_attribute: "",
        states_selected: [], // populated by jQuery upon select2 select
        races_selected: [], // populated by jQuery upon select2 select
        tags_selected: [], // populate by jQuery upon select2 select
        genders_selected: [], // populate by jQuery upon select2 select
        start_date: "", // populate by jQuery upon dp.change
        end_date: "", // populate by jQuery upon dp.change
        name: "", // two way binding for filter
        city: "", // two way binding for filter
        displayed_video: "",
        displayed_shooting: {},
        races: RACES, // used for filling select2
        states: STATES, // used for filling select2
        genders: GENDERS, // used for filling select2
        all_tags: ALL_TAGS, // used for filling select2
        shootings: SHOOTINGS,
        year: YEAR,
    },
    methods: {
        deleteShooting: DELETE_KILLING_FUNCTION,
        editShooting: EDIT_SHOOTING_FUNCTION,
        order_by: function(attribute) {
            /*Sets the order object that is used in the computed function for displaying killings
				
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
        resetFilters: function() {
            /*Resets the filter choices
				
            Sets 2-way-bound variables to their default values, and uses jQuery to reset non-2-way-bound variables

            Arguments:
            None

            Returns:
            None
            */
            var self = this;
            self.order_attribute = "";
            $.each(self.order, function(key, value) {
                self.order[key] = 0;
            });
            $("#state_select").val([]).trigger("change")
            $("#race_select").val([]).trigger("change")
            $("#tag_select").val([]).trigger("change")
            $("#gender_select").val([]).trigger("change");
            self.name = "";
            self.city = "";
            self.states_selected = [];
            self.genders_selected = [];
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
            var url = "{% url 'roster:date-index' date=1234 %}";
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
            var url = "{% url 'roster:date-index' date=1234 %}";
            url = url.replace("1234", year);
            return url;
        },
        openDetails: function(id) {
            /*Opens the details modal for a killing who's id matches the passed argument
            
            Iterates through killings to find the killing with the id that matches, and sets the
            displayed_shooting two way bound variable to that shooting so that it is autopopulated into the
            details modal, then opens the details modal
            
            Argument:
            :param id: the pk of a killing to be displayed
            
            Returns:
            None
            */
            shooting = this.shootings.find(function(shooting) {
                return shooting.id == id
            })
            this.displayed_shooting = shooting
            $('#shooting_details').modal('toggle');
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
        }
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
        displayed_shootings: function() {
            /*Calculates what shootings should be displayed to the user and returns the valid shootings
				
            Copies the list of shootings (so we don't affect the list)
            Filters by text, then city, then states, then genders, then races of the shooting,
            then tags, then start date, then end date, then orders them by the order attribute
            */
            var self = this;
            var displayed_shootings = this.shootings.slice();
            if (this.name.length > 0) {
                displayed_shootings = displayed_shootings.filter(function(shooting) {
                    if (shooting.name.toUpperCase().indexOf(self.name.toUpperCase()) > -1) {
                        return true;
                    } 
                })
            }
            if (this.city.length > 0) {
                displayed_shootings = displayed_shootings.filter(function(shooting) {
                    if (shooting.city.toUpperCase().indexOf(self.city.toUpperCase()) > -1) {
                        return true;
                    } 
                })
            }
            if (this.states_selected.length > 0) {
                displayed_shootings = displayed_shootings.filter(function(shooting) {
                    if (self.states_selected.indexOf("" + shooting.state_value) > -1) {
                        return true;
                    }
                })
            }
            if (this.genders_selected.length > 0) {
                displayed_shootings = displayed_shootings.filter(function(shooting) {
                    if (self.genders_selected.indexOf("" + shooting.gender_value) > -1) {
                        return true;
                    }
                })
            }
            if (this.races_selected.length > 0) {
                displayed_shootings = displayed_shootings.filter(function(shooting) {
                    if (self.races_selected.indexOf("" + shooting.race_value) > -1) {
                        return true;
                    }
                })
            }
            if (this.tags_selected.length > 0) {
                displayed_shootings = displayed_shootings.filter(function(shooting) {
                    for (var y = 0; y < shooting.tags.length; y++) {
                        if (self.tags_selected.indexOf("" + shooting.tags[y].text) > -1) {
                            return true;
                        }
                    }
                })
            }
            if (this.start_date.length != 0) {
                displayed_shootings = displayed_shootings.filter(function(shooting) {
                    var date = moment(shooting.date, "YYYY-MM-DD");
                    if (self.start_date < date) {
                        return true;
                    }
                })
            }
            if (this.end_date.length != 0) {
                displayed_shootings = displayed_shootings.filter(function(shooting) {
                    var date = moment(shooting.date, "YYYY-MM-DD");
                    if (self.end_date > date) {
                        return true;
                    }
                })
            }
            if (self.order_attribute != "") {
                order_order = self.order[self.order_attribute]; // 1 for ascending, -1 for descending
                if (order_order == 1) {
                    displayed_shootings.sort(function(a , b) {
                        if (self.order_attribute == "date") {
                            if (moment(a[self.order_attribute], "YYYY-MM-DD").isBefore(moment(b[self.order_attribute], "YYYY-MM-DD"))) {
                                return 1;
                            }
                            else if (moment(b[self.order_attribute], "YYYY-MM-DD").isBefore(moment(a[self.order_attribute], "YYYY-MM-DD"))) {
                                return -1;
                            }
                            return 0
                        }
                        else {
                            return a[self.order_attribute].localeCompare(b[self.order_attribute])
                        }
                    })
                }
                else {
                    displayed_shootings.sort(function(a , b) {
                        if (self.order_attribute == "date") {
                            if (moment(a[self.order_attribute], "YYYY-MM-DD").isBefore(moment(b[self.order_attribute], "YYYY-MM-DD"))) {
                                return -1;
                            }
                            else if (moment(b[self.order_attribute], "YYYY-MM-DD").isBefore(moment(a[self.order_attribute], "YYYY-MM-DD"))) {
                                return 1;
                            }
                            return 0
                        }
                        else {
                            return b[self.order_attribute].localeCompare(a[self.order_attribute])
                        }
                    })
                }
            }
            return displayed_shootings
        }
    }
})