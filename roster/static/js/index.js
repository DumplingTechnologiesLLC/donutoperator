

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
    $('#shooting_details').on('hidden.bs.modal', function () {
        stopVideo(document.getElementById("bodycam_video"))
    })
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
    setTimeout(function() {
        // since modern browsers ignore autcomplete=off (thanks...) we need to set it to
        // something they don't recognize to make it work properly
        $(".select2-search__field").attr("autocomplete", "aklsjehrfklasjhclkajsehf");
    }, 500)
})
Vue.component('paginate', VuejsPaginate)
Vue.component('date-picker', VueBootstrapDatetimePicker);
var vue_app = new Vue({
    el: '#app',
    delimiters: ["((","))"],
    data: {
        order: "-date",

        // pagination information
        totalPages: 0,
        startKilling: 0,
        endKilling: 0,
        maxKilling: 0,
        page: 1,
        pageSize: 50,
        loading: true,

        // filter by blanks
        noCity: false,
        noName: false,
        noAge: false,

        // used for calculating the age
        ageType: "range",
        lowerAge: "",
        upperAge: "",

        states_selected: [], // populated by jQuery upon select2 select
        races_selected: [], // populated by jQuery upon select2 select
        tags_selected: [], // populate by jQuery upon select2 select
        genders_selected: [], // populate by jQuery upon select2 select
        start_date: "", // populate by jQuery upon dp.change
        end_date: "", // populate by jQuery upon dp.change
        name: "", // two way binding for filter
        city: "", // two way binding for filter
        age: "", //two way binding for filter
        displayed_video: "",
        displayed_shooting: {},
        races: RACES, // used for filling select2
        states: STATES, // used for filling select2
        genders: GENDERS, // used for filling select2
        all_tags: ALL_TAGS, // used for filling select2
        shootings: [],
        year: YEAR,
    },
    mounted: function() {
        var self = this;
        self.filterShootings();
    },
    methods: {
        filterShootings: function(page) {
            var self = this;
            if (page) {
                self.page = page;
            }
            self.loading = true;
            self.shootings = [];
            $.get(SHOOTING_DATA_URL, this.queryParams).done(function(data) {
                self.shootings = data.shootings;
                self.maxKilling = data.maxKillings;
                self.startKilling = data.startKilling;
                self.endKilling = data.endKilling;
                self.totalPages = data.totalPages;
                self.loading = false;
            }).fail(function(data) {
                $.alert({
                    type: 'red',
                    title: "An error has occurred",
                    content: "We were unable to load the results. The server may be under heavy load or under maintenance. Please try again later."
                })
            });
        },
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
            if (this.order.indexOf(attribute) > -1) {
                if (this.order.indexOf("-") > -1) {
                    this.order = attribute
                }
                else {
                    this.order = "-" + attribute;
                }
            }
            else {
                this.order = '-' + attribute;
            }
            this.filterShootings(this.page);
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
            self.age = "";
            $('#start_date').datetimepicker('clear');
            $('#end_date').datetimepicker('clear');
            this.filterShootings();
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
            var url = YEAR_URL;
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
            var url = YEAR_URL;
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
        queryParams: function() {
            data = {
                "date__year": this.year,
                orderBy: this.order,
                pageSize: this.pageSize,
                page: this.page,
            }
            if (this.name && !this.noName) {
                data["name__icontains"] = this.name;
            }
            if (this.city && !this.noCity) {
                data["city__icontains"] = this.city;
            }
            if (this.states_selected.length > 0) {
                data["state__in"] = JSON.stringify(this.states_selected);
            }
            if (this.genders_selected.length > 0) {
                data["gender__in"] = JSON.stringify(this.genders_selected);
            }
            if (this.races_selected.length > 0) {
                data["race__in"] = JSON.stringify(this.races_selected);
            }
            if (this.tags_selected.length > 0) {
                data["tags__text__in"] = JSON.stringify(this.tags_selected);
            }
            if (this.start_date) {
                data["date__gte"] = this.start_date.format("YYYY-MM-DD");
            }
            if (this.end_date) {
                data["date__lte"] = this.end_date.format("YYYY-MM-DD");
            }
            if (this.noName) {
                data["name"] = "No Name";
            }
            if (this.noCity) {
                data["city"] = "No City";
            }
            if (this.ageType == "range" && !this.noAge) {
                if (this.lowerAge) {
                    data["age__gte"] = this.lowerAge;
                }
                if (this.upperAge) {
                    data["age__lte"] = this.upperAge;
                }
            }
            else {
                if (this.age) {
                    data["age"] = this.age;
                }
            }
            if (this.noAge) {
                data["age"] = -1;
            }
            return data;
        },
    }
})