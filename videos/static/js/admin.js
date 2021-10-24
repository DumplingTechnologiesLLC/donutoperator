Vue.component('multiselect', window.VueMultiselect.default);
Vue.use(Toasted, {
  iconPack: 'fontawesome', // set your iconPack, defaults to material. material|fontawesome|custom-class
});
const defaultVideo = {
  title: '',
  video: '',
  description: '',
  state: '',
  city: '',
  tags: [],
};
const youtubeRegex = /www.youtube.com\/watch\?v=[a-zA-Z0-9\-_]+/gi;

const VueAdminApp = new Vue({
  el: '#adminSection',
  delimiters: ['((', '))'],
  store: window.vuexStore,
  data: {
    states: STATES, // used for filling select2
    tags: ALL_TAGS, // used for filling select2
    video: defaultVideo,
    errors: {},
  },
  mounted() {
    setTimeout(() => {
      const multiselects = document.querySelectorAll('.multiselect');
      // for some god forsaken reason vue multiselect doesn't work properly and sets tabindex to -1.
      // so we need to manually fix this.
      multiselects.forEach((element) => {
        element.setAttribute('tabindex', 0);
      });
    }, 100);
  },
  watch: {
    storeEditedData: {
      handler(value) {
        this.video = JSON.parse(JSON.stringify(value));
      },
      deep: true,
    },
  },
  methods: {
    /**
     * @function closeModal
     */
    closeModal() {
      this.video = JSON.parse(JSON.stringify(defaultVideo));
      this.$set(this, 'errors', {});
    },

    /**
     * @function handleVideoTitle
     * @param {String} event the change event
     */
    handleVideoTitle(event) {
      const { value } = event.target;
      if (value.match(youtubeRegex)) {
        const [relevantPart] = value.split('&');
        this.video.video = relevantPart;
      } else {
        this.toast('Invalid URL format.', 'times');
      }
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
     * @function addTag
     * @param {String} newTag the text for the tag
     * @
     */
    addTag(newTag) {
      this.video.tags.push({
        text: newTag,
        display: newTag,
        value: newTag,
      });
    },

    /**
     * @function submitVideo
     * @listens onclick of submit
     */
    async submitVideo() {
      this.$set(this, 'errors', {});
      let stateValue = this.video.state?.value ?? null;
      if (stateValue !== null) {
        stateValue = parseInt(stateValue, 10);
      }
      const payload = { ...this.video, state: stateValue };
      console.log(payload);
      const url = this.video.id === undefined ? SERVER_URLS.items : `${SERVER_URLS.items}${this.video.id}/`;
      const action = this.video.id === undefined ? axios.post : axios.patch;
      const { error, message, icon, errors } = await this.$store.dispatch('submitVideo', {
        url,
        payload,
        action,
      });
      if (error) {
        this.$set(this, 'errors', errors);
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
      } else {
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
        if (this.video.id === undefined) {
          this.$set(this, 'video', defaultVideo);
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
  },
  computed: {
    modalTitle() {
      return this.video.id !== undefined ? 'Edit Video' : 'Add New Video';
    },
    submitText() {
      return this.video.id !== undefined ? 'Save changes' : 'Submit Video';
    },
    storeEditedData() {
      const data = JSON.parse(JSON.stringify(this.$store.state.editedVideo));
      if (typeof data.state === 'string') {
        const matchingState = STATES.find(s => s.display === data.state);
        data.state = JSON.parse(JSON.stringify(matchingState));
      }
      return data;
    },
  },
});
