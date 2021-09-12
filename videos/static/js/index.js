(() => {
  setTimeout(() => {
    const timeline = document.querySelector('.timeline-container');
    timeline.addEventListener('wheel', (e, delta) => {
      this.scrollLeft -= delta * 40;
      e.preventDefault();
    });
    const timelineCurrentYear = document.getElementById(`timelineYear${YEAR}`);
    timeline.scrollLeft = timelineCurrentYear.offsetLeft;
    // timelineCurrentYear.scrollIntoView({
    //     behavior: "smooth"
    // });
  }, 10);
})();

Vue.component('multiselect', window.VueMultiselect.default);
Vue.use(Toasted, {
  iconPack: 'fontawesome', // set your iconPack, defaults to material. material|fontawesome|custom-class
});
const VueApp = new Vue({
  el: '#app',
  delimiters: ['((', '))'],
  store: window.vuexStore,
  data: {
    states: STATES, // used for filling select2
    tags: ALL_TAGS, // used for filling select2
    year: YEAR,
  },
  mounted() {
    this.getItems();
    window.addEventListener('video-edit', this.handleEditClick);
    window.addEventListener('video-delete', this.handleDeleteClick);
  },
  methods: {
    /**
     * @function handleEditClick
     * @listens on-video-edit
     * @param {CustomEvent} event the edit event
     */
    handleEditClick(event) {
      const data = JSON.parse(event.detail.el.getAttribute('data-details'));
      this.$store.commit('setEditedVideo', data);
    },

    /**
     * @function handleDeleteClick
     * @listens on-video-delete
     * @param {CustomEvent} event the edit event
     */
    async handleDeleteClick(event) {
      if (confirm('Please confirm you wish to delete this video?')) {
        const data = JSON.parse(event.detail.el.getAttribute('data-details'));
        const error = await this.$store.dispatch('deleteItem', data.id);
        if (error) {
          this.toast(error, 'times');
        } else {
          this.toast('Video deleted successfully', 'check');
        }
      }
    },

    /**
     * passed to vue multiselect
     * @param {Object} option the option from the vue multiselect
     * @returns {String}
     */
    getDropdownLabel(option) {
      return option.display;
    },

    /**
     * @function updateFilter
     * @param {String} filter the filter to update
     * @param {String, Number, Array} value the value to set the filter to
     * @listens onchange of filter
     */
    updateFilter(filter, value) {
      this.$store.commit('setFilter', { filter, value });
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
      return (e.target.src = `https://i.ytimg.com/vi/${youtubeId}/mqdefault.jpg`);
    },

    /**
     * @function resetFilters
     * @listens onclick of reset button
     * Resets all the 2 way bound variables
     */
    resetFilters() {
      this.$store.commit('resetFilters');
      this.getItems();
    },

    /**
     * @function toast
     * @param {String} message the message to toast
     * @param {String} icon the icon for the toast
     */
    toast(message, icon) {
      this.$toasted.show(message, {
        action: {
          text: 'Close',
          onClick(e, toastObject) {
            toastObject.goAway(0);
          },
        },
        icon: {
          name: icon,
        },
      });
    },

    /**
     * @function getItems
     * @listens onclick of submit button
     * Reaches out to API and requests videos
     */
    getItems: async function () {
      const error = await this.$store.dispatch('fetchItems');
      if (error) {
        this.toast(error, 'times');
      }
    },

    /**
     * @function calculateNextYear
     * @listens onclick of timeline right arrow
     * @returns {String} url for next year
     */
    calculateNextYear() {
      const year = moment(YEAR, 'YYYY').add(1, 'y').format('YYYY');
      return SERVER_URLS.dateIndex.replace('1234', year);
    },

    /**
     * @function calculatePreviousYear
     * @listens onclick of timeline left arrow
     * @returns {String} url for next year
     */
    calculatePreviousYear() {
      const year = moment(YEAR, 'YYYY').subtract(1, 'y').format('YYYY');
      return SERVER_URLS.dateIndex.replace('1234', year);
    },
  },
  computed: {
    filters() {
      return this.$store.state.filters;
    },
    inFlight() {
      return this.$store.state.inFlight;
    },
    videos() {
      return this.$store.state.items;
    },
    currentYear() {
      return moment().format('YYYY');
    },
  },
});
