import Vue from 'vue'
import App from './App.vue'
import MutaObjectView from './MutaObjectView.vue';
import VueRouter from 'vue-router';
import Vuex from 'vuex';
import 'babel-polyfill';
import { globalPropId, isDynamic } from './utils';
import _ from 'lodash';

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
        mutaObjectList: [],
        mutaObjects: {},
        mutaProps: {},
        selectedObjectId: null
    },
    mutations: {
        set_muta_objects (state, objects) {
            state.mutaObjectList = objects;
        },
        set_selected_object_id (state, selectedObjectId) {
            state.selectedObjectId = selectedObjectId
        },
        set_muta_object (state, mutaObject) {
            console.log("Commiting");
            console.log(mutaObject);
            Vue.set(state.mutaObjects, mutaObject.obj_id, mutaObject);
            // Parse all props in to the normalized all-object prop array
            for (let prop of mutaObject.props) {
                // let propId = globalPropId(mutaObject.obj_id, prop.id);
                let propId = globalPropId(_.get(prop, 'class_scope', false)?
                    mutaObject.class_id:mutaObject.obj_id, prop.id);

                Vue.set(state.mutaProps, propId,
                        { "value": prop.value, "eventSource": null});
                console.log("PropID: " + propId);
                // Vue.set(state.mutaProps, globalPropId(mutaObject.obj_id, prop.id),
                //     { "value": prop.value, "eventSource": null});
          }
        },
        muta_prop_change (state, mutaPropChange) {
            // console.log("Storing prop change");
            Vue.set(state.mutaProps,
                globalPropId( mutaPropChange.objId, mutaPropChange.propId),
                { "value": mutaPropChange.value,
                  "eventSource": mutaPropChange.eventSource }
                  );
        }
    },
    getters: {
        mutaObjectCount: state => {
            return state.mutaObjectList.length;
        },
        getMutaProp: (state) => (objId, propId) => {
            return _.find(state.mutaObjects[objId].props, {'id': propId});
        },
        getMutaPropValue: (state, getters) => (objId, propId) => {
            let scope_objId = null;
            if (_.get(getters.getMutaProp(objId, propId),
                    'class_scope', false)) {
                scope_objId = state.mutaObjects[objId].class_id;
            } else {
                scope_objId = objId;
            }
            return state.mutaProps[globalPropId(scope_objId, propId)].value;
        },
        getMutaPropChange: (state) => (objId, propId) => {
            return state.mutaProps[globalPropId(objId, propId)];
        },
        getDynamicValue: (state, getters) => (objId, value) => {
            if (isDynamic(value)) {
                return getters.getMutaPropValue(objId, value.id);
            } else {
                return value;
            }
        }
    }
})

new Vue({
  // el: '#app',
  render: h => h(App),
    router,
    store
}).$mount('#app');
