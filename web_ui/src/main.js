import Vue from 'vue'
import App from './App.vue'
import MutaObjectView from './MutaObjectView.vue';
import VueRouter from 'vue-router';
import 'babel-polyfill';

Vue.use(VueRouter);

//https://github.com/vuejs/vue/issues/1768#issuecomment-241787513
window.eventBus = new Vue();

const router = new VueRouter({
    history: false,
    routes: [{ path: '/objects/:id', name: 'object', component: MutaObjectView },
        { path: '/objects', component: MutaObjectView },
        {path: '/', redirect:'/objects'}]
});

new Vue({
  // el: '#app',
  render: h => h(App),
    router
}).$mount('#app');
