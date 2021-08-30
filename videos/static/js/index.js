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
(() => {
    setTimeout(() => {
        const timeline = document.querySelector('.timeline-container');
        timeline.addEventListener('wheel', (e, delta) => {
            this.scrollLeft -= (delta * 40);
            e.preventDefault();
        })
        const timelineCurrentYear = document.getElementById(`timelineYear${YEAR}`);
        timelineCurrentYear.scrollIntoView({
            behavior: "smooth"
        });
    }, 1000)
})()

Vue.component('multiselect', window.VueMultiselect.default);
Vue.use(Toasted, {
    iconPack : 'fontawesome' // set your iconPack, defaults to material. material|fontawesome|custom-class
});
const VueApp = new Vue({
    el: '#app',
    delimiters: ["((","))"],
    data: {
        city: "",
        text: "",
        selectedStates: [],
        selectedTags: [],
        startDate: "",
        endDate: "",
        inFlight: false,
        states: STATES, // used for filling select2
        tags: ALL_TAGS, // used for filling select2
        year: YEAR,
        videos: [],
    },
    mounted() {
        this.getItems();
    },
    methods: {


        /**
         * passed to vue multiselect
         * @param {Object} option the option from the vue multiselect
         * @returns {String}
         */
        getDropdownLabel(option) {
            return option.display
        },

        /**
         * @function generateThumbnail
         * @param {String} youtubeUrl 
         * @returns {String} image url
         * Returns the webp thumbnail for a video
         */
        generateThumbnail(youtubeUrl) {
            const [, youtubeId] = youtubeUrl.split('watch?v=');
            return `https://i.ytimg.com/vi_webp/${youtubeId}/mqdefault.webp`;
        },

        /**
         * @function generateBackupThumbnail
         * @param {String} youtubeUrl 
         * @returns {String} image url
         * Returns the webp thumbnail for a video
         */
        generateBackupThumbnail(e, youtubeUrl) {
            const [, youtubeId] = youtubeUrl.split('watch?v=');
            return e.target.src = `https://i.ytimg.com/vi/${youtubeId}/mqdefault.jpg`;
        },

        /**
         * @function resetFilters
         * @listens onclick of reset button
         * Resets all the 2 way bound variables
         */
        resetFilters() {
            this.text = "";
            this.city = "";
            this.selectedStates = [];
            this.selectedTags = [];
            this.startDate = "";
            this.endDate = "";
            this.getItems();
        },

        /**
         * @function getItems
         * @listens onclick of submit button
         * Reaches out to API and requests videos
         */
        getItems: async function() {
            this.inFlight = true;
            this.videos = [];
            console.log(this.computedParams)
            try {
                const response = await axios.get(SERVER_URLS.items, {
                    params: this.computedParams
                });
                this.inFlight = false;
                if (response.status === 200) {
                    this.videos = response.data.slice();
                } else {
                    this.$toasted.show(
                        'A server error has occurred', {
                        icon : {
                            name : 'times'
                        }
                    });    
                }
            } catch (error) {
                this.inFlight = false;
                this.$toasted.show(
                    'A network error has occurred', {
                        icon : {
                            name : 'times'
                        }
                });
            }
        },

        /**
         * @function calculateNextYear
         * @listens onclick of timeline right arrow
         * @returns {String} url for next year
         */
        calculateNextYear() {
            const year = moment(YEAR, "YYYY").add(1, "y").format("YYYY")
            return SERVER_URLS.dateIndex.replace('1234', year);
        },

        /**
         * @function calculatePreviousYear
         * @listens onclick of timeline left arrow
         * @returns {String} url for next year
         */
        calculatePreviousYear() {
            const year = moment(YEAR, "YYYY").subtract(1, "y").format("YYYY")  
            return SERVER_URLS.dateIndex.replace('1234', year);
        },
    },
    computed: {
        computedParams() {
            const params = {
                tags: this.selectedTags.map((tag) => tag.value),
                date__year: YEAR,
            };
            if (this.text) {
                params.title__icontains = this.text;
                params.description__icontains = this.text;
            }
            if (this.city) {
                params.city__icontains = this.city;
            }
            if (this.selectedStates.length) {
                params.state__in = this.selectedStates.map((state) => state.value)
            }
            if (this.startDate) {
                params.date__gte = moment(this.startDate).format('YYYY-MM-DD')
            }
            if (this.endDate) {
                params.date__gte = moment(this.endDate).format('YYYY-MM-DD')
            }
            return params;
        },
        currentYear() {
            return moment().format("YYYY")
        },
    }
})