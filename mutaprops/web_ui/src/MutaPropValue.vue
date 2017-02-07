<template>
    <span class="pull-right form-inline">
        <label :class="labelClass" v-if="isChangeLabelVisible">
            {{ labelVal }}
        </label>
        <template v-if="hasSelect">
            <select  :disabled="propObject.read_only" class="form-control" v-model="uiVal"
            :class="inputClass" v-on:change="onUserChange"
                     v-on:click="onSelectClick">
                <option v-for="option in selectItems"
                        v-bind:value="option.value">
                    {{ option.text }}
                </option>
            </select>
        </template>
        <template v-else>
            <input v-if="(propObject.value_type == 'INT') || (propObject.value_type == 'REAL')"
                   v-model.number="val" type="number"
                   :min="propObject.min_val" :max="propObject.max_val" :step="propObject.step"
                   :disabled="propObject.read_only" class="form-control"
                   :class="inputClass"
                   v-on:change="onUserChange" v-on:keyup.enter="onUserChange">
            <input v-if="propObject.value_type == 'BOOL'" type="checkbox" data-toggle="propObject.toggle"
                   v-model="val" :class="inputClass" v-on:change="onUserChange"
                   :disabled="propObject.read_only" :id="validId">
            <input v-if="propObject.value_type == 'STRING'" v-model="val" type="text"
                   :class="inputClass" :disabled="propObject.read_only"
                   :maxlength="propObject.max_val" class="form-control"
                   v-on:change="onUserChange" v-on:keyup.enter="onUserChange">
            <button v-if="propObject.type == 'action'" v-on:click="actionExecuted"
                    type="button"
                    class="btn btn-primary">
                Action
            </button>
        </template>
    </span>
</template>

<script>
    /**
     * The main thing here is to understand that we have to manage two independent
     * value variables:
     *  1. The value which is set in the ui (uiVal)
     *  2. The value which is set in the underlying object (objectVal)
     *
     *  Ideally, uiVal == objectVal, but during user changes, these two have
     *  different values.
     *
     *  uiVal can be changed by user interaction and also by changes coming from
     *  the underlying object. It is stored within this component.
     *  objectVal can be only changed by the underlying object, and is stored
     *  in the Vuex store.
     *
     *  The value change flows are also of two types:
     *   1. User-initiated change
     *   2. External-change (either initiated by an object change, or by
     *      other-user change in case more than one UI is connected to
     *      the same object).
     *
     *  In case of User-initiated change, the UI goes through following stages:
     *  [currentValue(original)] --(user starts changing)-->[inUserChange]--
     *  --(user finished changin)-->[inObjectUpdate]--(objectUpdated)--
     *  -->[currentValue(new)]
     *  So there are three discrete states, in which the UI must behave
     *  differently:
     *
     *  currentValue - UI looks normal.
     *               - if an external change occurs at this moment, it's reflected
     *               in the UI widger, and side label shows the past values.
     *               Color code of the label show whether the external change
     *               is object initiated, or other-user initiated.
     *               In case of other-user initiated event, it's also possible
     *               to distinguis, if the event was initiated by master UI
     *               or other UI (this is only useful in chained UI's).
     *
     *  inUserChange - the background of the UI should change (orange) to reflect
     *  that the field is being edited.
     *               - a side label (orange) displays the last valid value
     *                 before user started changing it
     *               - if an external change occurs at this moment, it's
     *                 only reflected in the side label
     *
     *  inObjectUpdate - the background of the UI should change (red) to reflect
     *  that the field is now awaiting object confirmation.
     *                 - if an external change occurs at this moment, it's
     *                   only reflected in the side label
     */
    import Vue from 'vue';
    import _ from 'lodash';
    import slugify from 'slugify';
    import Resource from 'vue-resource';
    import { globalPropId, isDynamic, parseSelectData } from './utils';
    import { mapState } from 'vuex';
    Vue.use(Resource);

    export default {
        props: ['propObject', 'objId'],
        data: function() {
            return {
                labelVal: this.propObject.value,
                uiVal: null,
                valueState: 'current',
                inUserChange: false,
                inObjectChange: false,
                afterSelectUpdate: false,
                afterObjectChange: false,
                inModelUpdate: false,
                dynamicSelectId: null,
                dynamicSelectClassId: null,
                changeMode:null,
            }
        },
        computed: {
            objectVal: function() {
//              return this.$store.state.mutaProps[globalPropId(this.objId,
//                    this.propObject.id)];
              return this.$store.getters.getMutaPropValue(this.objId,
                        this.propObject.id);
            },
            displayVal: function() {
              return this.displayValue(this.val);
            },
            selectItems: function () {
              console.log("Parsing select data for " + this.propObject.id);
              return parseSelectData(
                  this.$store.getters.getDynamicValue(this.objId,
                    this.propObject.select));
            },
            isChangeLabelVisible: function() {
                return (this.inUserChange || this.afterObjectChange ||
                this.afterSelectUpdate);
            },
            validId : function() {
                return slugify(this.propObject.id);
            },
            hasSelect: function() {
                // TODO: Add dynamic source
                return !_.isEmpty(this.propObject.select);
            },
            labelClass: function() {
                var labelType = '';
                if (this.inUserChange) {
                    labelType = 'label-warning';
                }
                if (this.afterObjectChange || this.afterSelectUpdate) {
                    labelType = 'label-primary';
                }
                if ((this.changeMode == 'user') ||
                    (this.changeMode == 'master')) {
                    labelType = 'label-info';
                }
                return ['label', 'label-valchange', labelType];
            },
            inputClass: function() {
                if (this.inModelUpdate) {
                    return 'updating-value';
                }

                if (this.inUserChange) {
                    return 'unset-value';
                }

                return '';
            },
//            mapState({
//              val (state) {
//                return state.mutaProps[globalPropId(this.objId, this.propObject.id)];
//              }
//            })
        },
        watch: {
            val: function(value, oldValue) {
                if (this.inObjectChange) {
                    this.inObjectChange = false;
                    this.afterObjectChange = true;
                } else {
                    if (!this.inUserChange) {
                        this.labelVal = this.displayValue(oldValue);
                        this.inUserChange = true;
                        this.afterObjectChange = false;
                    }
                }
            }
        },
        methods: {
            actionExecuted: function() {
                var vm = this;
                this.$http.put('api/objects/' + encodeURIComponent(this.objId) +
                        '/props/' + encodeURIComponent(this.propObject.id) + '/action')
                        .then((response)=> {
                    console.log("Action executed object:" + this.objId +
                            " action:" + this.propObject.id);
                },(response) => {
                    console.log(response)
                });
            },
            onUserChange: _.debounce(function() {
                // Update the value
                console.log("Updating object " + this.objId + " prop " +
                        this.propObject.id + " with value " + this.val);
                this.afterSelectUpdate = false;
                this.inModelUpdate = true;
                var vm = this;
                this.$http.put('api/objects/' + encodeURIComponent(this.objId) +
                        '/props/' + encodeURIComponent(this.propObject.id) + '?value=' +
                        encodeURIComponent(this.val)).then((response)=> {
                    vm.inUserChange = false;
                    vm.afterObjectChange = false;
                    vm.inModelUpdate = false;
                    console.log("Updated object " + this.objId + " prop " +
                            this.propObject.id + " with value " + this.val);
                },(response) => {
                    console.log(response);
                });
            }, 1000),
            onSelectClick: function() {
                this.afterSelectUpdate = false;
            },
            getSelectText: function(selectVal) {
//                console.log("Getting text for value " + selectVal + " from this " + this.selectItems);
//                console.log(this.selectItems)
                var temp = _.find(this.selectItems, ['value', selectVal]);
                return (temp)?temp.text:'Undefined';
            },
            displayValue: function(value) {
//                console.log("Making display value for: " + value);
//                console.log(this.propObject.id + " has select: " + this.hasSelect);
                var temp = this.hasSelect?this.getSelectText(value):value;
                console.log("Display value for " + this.propObject.id +
                    " is " + temp);
                return temp;
//                return this.hasSelect?this.getSelectText(value):value;
            }
        },
        created: function() {

            //Prepare notification processing
            var vm = this;
            window.eventBus.$on('property_change', function(params) {
                vm.$store.commit('muta_prop_change', params);
//                console.log("Even fired")
//                vm.$store.getters.getMutaPropValue(vm.objId, params.propId)
                if ((params.objId == vm.objId) && (params.propId == vm.propObject.id)) {
                    if ((params.eventSource == 'user') && (vm.inModelUpdate)) {
                        //Ignore this, because it's most likely just a
                        // notification which was caused by the same user
                        // There is however a small probability that
                        // Two user changes from different UI instances
                        // At the same time would go unnoticed.
                        // The only solution for this is to ID the
                        // UI, but that is too much for this release.
                        return;
                    }
                    vm.changeMode = params.eventSource;
                    vm.inObjectChange = true;
                    if (vm.inUserChange) {
                        //Don't change the value just the label
                        vm.labelVal = vm.displayValue(params.value);
                        vm.afterObjectChange = true;
                    } else {
                        vm.labelVal = vm.displayValue(vm.val);
//                        vm.val = params.value;

                        //For the infamous bootstrap toggle
                        if (vm.propObject.value_type === 'BOOL') {
                            var toggle = $("input[type='checkbox']#" +
                                vm.validId);
                            toggle.bootstrapToggle(vm.val ? 'on' : 'off');
                        }
                    }
                }
            });
//            if (this.dynamicSelectId != null) {
//                window.eventBus.$on('select_change', function(params) {
//                    var temp_id;
//                    if (vm.dynamicSelectClassId != null) {
//                       temp_id = vm.dynamicSelectClassId;
//                    } else {
//                        temp_id = vm.objId;
//                    }
//
//                    if ((params.objId == temp_id) &&
//                            (params.selectId == vm.dynamicSelectId)) {
//                        vm.updateSelectItems(params.value);
//                        vm.labelVal = "Selection Updated";
//                        vm.afterSelectUpdate = true;
//                    }
//                });
//            }
        },
        mounted: function () {
            // If we use toggle instead of checkbox, we have to manually service all stuff
            // that Vue is doing automatically by itself, because the way toggle is made,
            // it destroys all Vue bindings...
            if (this.propObject.value_type === 'BOOL') {
                var self = this;
                var toggle = $("input[type='checkbox']#" + this.validId);
                console.log("Creating toggle");
                console.log(this.propObject.toggle);
                toggle.bootstrapToggle( this.propObject.toggle );
                toggle.change(function () {
                    self.val = toggle.prop('checked');
                    self.onUserChange();
                    //TODO: check why is it registering as remoteChange and not userChange
                    //TODO: Add selection between checkbox and Toggle
                })

            }

        }
    }

</script>

<style>
    .unset-value {
        background-color: rgba(240,173,78, 0.3);
    }
    .updating-value {
        background-color: rgba(237, 77, 43, 0.3);
    }

    .label-valchange {
        margin-right: 8px;
    }
</style>
