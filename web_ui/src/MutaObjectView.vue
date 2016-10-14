<template>
    <div id="wrapper">
        <muta-object-list v-if="mutaObjects.length > 1"
                          v-bind:object-list="mutaObjects"
                          v-bind:selected-object="definedObject()">
        </muta-object-list>
        <!--TODO: Solve for no object selected and only one object in the list -->
        <div id="main-wrapper"
             :class="[(mutaObjects.length>1)?'col-md-10':'col-md-12', 'pull-right']">
            <div id="main" v-if="definedObject()">
                <div class="page-header" v-if="mutaObjects.length == 1">
                    <h3>{{ definedObject() }}</h3>
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
                <muta-prop-list v-bind:prop-list="mutaProps"
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
import BeatLoader from 'vue-spinner/src/BeatLoader.vue';
Vue.use(Resource);

export default {
    components: { MutaObjectList, MutaPropList, BeatLoader },
    data: function() {
        return {
            mutaProps: [],
            mutaObjects: [],
            mutaListLoaded: false,
            mutaObjectAvailable: true
        }
    },

    methods: {
        fetchObjects: function() {
            var vm = this
            this.$http.get('api/objects').then((response)=> {
                console.log(response.body);
                vm.mutaObjects = response.body;
                vm.updateRedirect();
            },(response) => {
                console.log(response)
            });
        },

        fetchProps: function(objId) {
            var vm = this;
            var propResource = this.$resource('api/objects/{id}/props');
            this.mutaListLoaded = false;
            this.mutaObjectAvailable = true;
            propResource.get({id:objId}).then((response)=> {
                vm.mutaProps = response.body;
                vm.mutaListLoaded = true;
            },(response) => {
                console.log(response)
                vm.mutaListLoaded = true;
                vm.mutaObjectAvailable = false;
            });
        },

        definedObject: function() {
            if (this.$route.params.hasOwnProperty('id')) {
                return this.$route.params.id;
            } else {
                return null;
            }
        },

        updateRedirect: function() {
            if ((this.definedObject() == null) && (this.mutaObjects.length == 1)) {
                console.log("Now we shall redirect")
                this.$router.push({ name: 'object', params: { id: this.mutaObjects[0]}});
            }
        }

    },
    created: function() {
        console.log("Called created.");
        this.fetchObjects();
        this.fetchProps(this.definedObject());
        console.log(this.definedObject());
    },

    watch: {
        $route: function () {
            // TODO: This should go away when websockets are implemented.
            var dObj = this.definedObject();
            if (dObj) {
                this.fetchProps(this.definedObject());
            }

            if (this.$route.path == '/objects') {
                this.updateRedirect();
            }
        }
    },
}
</script>

<style>
#main {
    padding-top: 40px;
}
</style>