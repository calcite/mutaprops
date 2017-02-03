import Vue from 'vue'
import App from './App.vue'
import MutaObjectView from './MutaObjectView.vue';
import VueRouter from 'vue-router';
import Vuex from 'vuex';
import 'babel-polyfill';

Vue.use(VueRouter);
Vue.use(Vuex);

//https://github.com/vuejs/vue/issues/1768#issuecomment-241787513
window.eventBus = new Vue();

const router = new VueRouter({
    history: false,
    routes: [{ path: '/objects/:id', name: 'object', component: MutaObjectView },
        { path: '/objects', component: MutaObjectView },
        {path: '/', redirect:'/objects'}]
});

const store = new Vuex.Store({
    state: {
        mutaObjects: [],
        selectedObjectId: null
    },
    mutations: {
        set_muta_objects (state, objects) {
            state.mutaObjects = objects;
        },
        set_selected_object_id (state, selectedObjectId) {
            state.selectedObjectId = selectedObjectId
        }
    },
    getters: {
        mutaObjectCount: state => {
            return state.mutaObjects.length;
        }
    }
})

new Vue({
  // el: '#app',
  render: h => h(App),
    router,
    store
}).$mount('#app');
