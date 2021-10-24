Vue.component('multiselect', window.VueMultiselect.default);
Vue.component('pagination', window.Pagination);
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
    pageSize: PAGE_SIZE, // set by the server in index.html
    paginationOptions: {
      chunk: 5,
      theme: 'bootstrap4',
    }
  },
  mounted() {
    this.getItems();
    window.addEventListener('video-edit', this.handleEditClick);
    window.addEventListener('video-delete', this.handleDeleteClick);
  },
  methods: {
    /**
     * @function handlePagination
     * @param {Number} page - The page that was selected 
     */
     handlePagination(page) {
      this.$store.commit('setPagination', { key: 'page', value: page });
      this.getItems();
    },

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
  },
  computed: {
    pagination() {
      return this.$store.state.pagination
    },
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
