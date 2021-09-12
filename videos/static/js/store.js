Vue.use(Vuex);

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

window.vuexStore = new Vuex.Store({
  state: {
    filters: {
      city: '',
      text: '',
      selectedStates: [],
      selectedTags: [],
      startDate: '',
      endDate: '',
    },
    editedVideo: {},
    items: [],
    inFlight: false,
  },
  mutations: {
    setEditedVideo(state, data) {
      Vue.set(state, 'editedVideo', data);
    },
    setModalVisible(state, data) {
      Vue.set(state, 'modalVisible', data);
    },
    setInFlight(state, value) {
      state.inFlight = value;
    },
    setFilter(state, { filter, value }) {
      Vue.set(state.filters, filter, value);
    },
    setItems(state, items) {
      Vue.set(state, 'items', items);
    },
    resetFilters(state) {
      Vue.set(state.filters, 'text', '');
      Vue.set(state.filters, 'city', '');
      Vue.set(state.filters, 'selectedStates', []);
      Vue.set(state.filters, 'selectedTags', []);
      Vue.set(state.filters, 'startDate', '');
      Vue.set(state.filters, 'endDate', '');
    },
  },
  actions: {
    async deleteItem(context, id) {
      context.commit('setInFlight', true);
      try {
        await axios.delete(
          `${SERVER_URLS.items}${id}`,
          { id },
          {
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken'),
            },
          }
        );
        context.dispatch('setItems');
        return true;
      } catch (error) {
        context.commit('setInFlight', false);
        return 'An error occurred while trying to delete the video. Contact the administrator.';
      }
    },
    async fetchItems(context) {
      context.commit('setInFlight', true);
      context.commit('setItems', []);
      try {
        const response = await axios.get(SERVER_URLS.items, {
          params: context.getters.computedParams,
        });
        context.commit('setInFlight', false);
        if (response.status === 200) {
          context.commit('setItems', response.data.slice());
          return false;
        } else {
          return 'A server error has occurred';
        }
      } catch (error) {
        context.commit('setInFlight', false);
        return 'A network error has occurred';
      }
    },
    async submitVideo(context, { url, payload, action }) {
      context.commit('setInFlight', true);
      try {
        const response = await action(url, payload, {
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
        });
        context.commit('setInFlight', false);
        if ([201, 200].some((status) => status === response.status)) {
          context.dispatch('fetchItems');
          return {
            error: false,
            message: payload.id !== undefined ? 'Video updated successfully' : 'Video created sucessfully',
            icon: 'check',
            errors: {},
          };
        }
      } catch (error) {
        context.commit('setInFlight', false);
        if (!error.response) {
          return { error: true, message: 'A network error has occurred', icon: 'times', errors: {} };
        } else if (error.response.status === 400) {
          return {
            error: true,
            message: 'There was a problem with your submission. Review your inputs',
            icon: 'exclamation-circle',
            errors: error.response.data,
          };
        } else {
          return { error: true, message: 'A server error has occurred', icon: 'times', errors: {} };
        }
      }
    },
  },
  getters: {
    computedParams(state) {
      const params = {
        tags: state.filters.selectedTags.map((tag) => tag.value),
        date__year: YEAR,
      };
      if (state.filters.text) {
        params.title__icontains = state.filters.text;
        params.description__icontains = state.filters.text;
      }
      if (state.filters.city) {
        params.city__icontains = state.filters.city;
      }
      if (state.filters.selectedStates.length) {
        params.state__in = state.filters.selectedStates.map((state) => state.filters.value);
      }
      if (state.filters.startDate) {
        params.date__gte = moment(state.filters.startDate).format('YYYY-MM-DD');
      }
      if (state.filters.endDate) {
        params.date__gte = moment(state.filters.endDate).format('YYYY-MM-DD');
      }
      return params;
    },
  },
});
