<template>
    <div id="wrapper">
        <muta-object-list v-if="$store.getters.mutaObjectCount > 1"
                          v-bind:object-list="$store.state.mutaObjects"
                          v-bind:selected-object="viewedObjectId">
        </muta-object-list>
        <!--TODO: Solve for no object selected and only one object in the list -->
        <div id="main-wrapper"
             :class="[($store.getters.mutaObjectCount > 1)?'col-md-10':'col-md-12',
             'pull-right']">
            <div id="main" v-if="viewedObjectId">
                <div class="page-header">
                    <h3>{{ viewedObjectId }}</h3>
                </div>
                <div v-if="!mutaListLoaded" class="text-center">
                    <beat-loader :loading="!mutaListLoaded"
                                 color="#003394" height="200px" width="200px">

                    </beat-loader>
                </div>
                <div v-if="!mutaObjectAvailable">
                    <div class="alert alert-danger" role="alert">
                        <strong>Error!</strong> Object is not available.
                    </div>
                </div>
                <div v-if="mutaObjectAvailable && !objectConnectionExists">
                    <div class="alert alert-danger" role="alert">
                        <strong>Connection to object lost!</strong>
                        Changes will not be applied.
                    </div>
                </div>
                <muta-prop-list v-bind:prop-list="mutaProps"
                                :obj-id="viewedObjectId"
                                v-if="mutaListLoaded && mutaObjectAvailable">
                </muta-prop-list>
            </div>
            <div id="main" v-else>
                <div class="alert alert-info" role="alert">
                    Select an object to control.
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import MutaObjectList from './MutaObjectList.vue'
import MutaPropList from './MutaPropList.vue'
import Vue from 'vue';
import Resource from 'vue-resource';
import _ from 'lodash';
import BeatLoader from 'vue-spinner/src/BeatLoader.vue';
Vue.use(Resource);

export default {
    components: { MutaObjectList, MutaPropList, BeatLoader },
    data: function() {
        return {
            mutaProps: [],
            mutaObjects: [],
            mutaListLoaded: false,
            mutaObjectAvailable: true,
            objectConnectionExists: true,
        }
    },
    computed: {
      viewedObjectId: function () {
          if (this.$route.params.hasOwnProperty('id')) {
              return this.$route.params.id;
          } else {
              return null;
          }
      },
      objectConnectionExists: function () {
        return _.includes(this.$store.state.mutaObjects, this.viewedObjectId);
      }
    },
    methods: {

//        fetchProps: function(objId) {
//            var vm = this;
//            var propResource = this.$resource('api/objects/{id}/props');
//            this.mutaListLoaded = false;
//            this.mutaObjectAvailable = true;
//            propResource.get({id:objId}).then((response)=> {
//                vm.mutaProps = response.body;
//                vm.mutaListLoaded = true;
//                vm.objectConnectionExists = true;
//            },(response) => {
//                vm.mutaListLoaded = true;
//                vm.mutaObjectAvailable = false;
//            });
//        },

        fetchObject: function(objId) {
            var vm = this;
            var objResource = this.$resource('api/objects/{id}');
            this.mutaListLoaded = false;
            this.mutaObjectAvailable = true;
            objResource.get({id:objId}).then((response)=> {
                vm.mutaProps = response.body.props;
                vm.mutaListLoaded = true;
                vm.objectConnectionExists = true;
                vm.$store.commit('set_muta_object', response.body);
            },(response) => {
                vm.mutaListLoaded = true;
                vm.mutaObjectAvailable = false;
            });
        },

        updateRedirect: function() {
            if ((this.viewedObjectId == null) &&
                    (this.$store.getters.mutaObjectCount == 1)) {
                console.log("Now we shall redirect");
                this.$router.push({ name: 'object',
                                    params: {
                                        id: this.$store.state.mutaObjects[0]
                                            }
                                  });
            }
        },

    },
    created: function() {
//        this.fetchObjects();
        var vm = this;
        this.$store.watch(function (state) {
          return state.mutaObjects;
        }, () => {
            if ((vm.$store.state.selectedObjectId == null) &&
                (vm.$store.getters.mutaObjectCount == 1)) {
                vm.$router.push({
                    name: 'object',
                    params: {id: vm.$store.state.mutaObjects[0]}
                });
            }
        });
        this.$store.commit('set_selected_object_id', this.viewedObjectId);
//        this.fetchProps(this.viewedObjectId);
        this.fetchObject(this.viewedObjectId);
    },

    watch: {
        $route: function () {
            var dObj = this.viewedObjectId;
            if (dObj) {
                this.fetchObject(this.viewedObjectId);
            }

            if (this.$route.path == '/objects') {
                this.updateRedirect();
            }
        },
    },
}
</script>

<style>
#main {
    padding-top: 40px;
}
.page-header {
    margin-top: -20px;
}
#wrapper {
    min-height: 100%;
    height: 100%;
    width: 100%;
    position: absolute;
    top: 0px;
    left: 0;
    display: inline-block;
}
#main-wrapper {
    height: 100%;
    overflow-y: auto;
    padding: 50px 0 0px 0;
}
#sidebar-wrapper {
    height: 100%;
    padding: 50px 0 0px 0;
    position: fixed;
    border-right: 1px solid gray;
}
#sidebar {
    position: relative;
    height: 100%;
    overflow-y: auto;
}
#sidebar .list-group-item {
    border-radius: 0;
    border-left: 0;
    border-right: 0;
    border-top: 0;
}
</style>
