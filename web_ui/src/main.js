import Vue from 'vue'
import App from './App.vue'
import MutaObjectView from './MutaObjectView.vue';
import VueRouter from 'vue-router';

Vue.use(VueRouter);

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
