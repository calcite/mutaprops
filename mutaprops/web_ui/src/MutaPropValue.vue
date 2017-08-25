<template>
    <span class="pull-right form-inline">
        <label :class="labelClass" v-if="isChangeLabelVisible">
            {{ labelVal }}
        </label>
        <template v-if="hasSelect">
            <select  :disabled="read_only" class="form-control" v-model="uiVal"
            :class="inputClass" v-on:change="onUserChange"
                     v-on:click="onSelectClick">
                <option v-for="option in selectItems"
                        v-bind:value="option.value">
                    {{ option.text }}
                </option>
            </select>
        </template>
        <template v-else>
            <input v-if="(propObject.value_type == 'INT') ||
                         (propObject.value_type == 'REAL')"
                   v-model.number="uiVal" type="number"
                   :min="min_val" :max="max_val" :step="step"
                   :disabled="read_only" class="form-control"
                   :class="inputClass"
                   v-on:change="onUserChange" v-on:keyup.enter="onUserChange">
            <input v-if="propObject.value_type == 'BOOL'" type="checkbox"
                   v-model="uiVal" :class="inputClass"
                   v-on:change="onUserChange"
                   :disabled="read_only" :id="validId">
            <input v-if="propObject.value_type == 'STRING'" v-model="uiVal"
                   type="text" :class="inputClass" :disabled="read_only"
                   :maxlength="max_val" class="form-control"
                   v-on:change="onUserChange" v-on:keyup.enter="onUserChange">
            <button v-if="propObject.type == 'action'"
                    v-on:click="actionExecuted" type="button"
                    :disabled="read_only" class="btn btn-primary">
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
                uiVal: this.propObject.value,
                inUserChange: false,
                inObjectChange: false,
                afterObjectChange: false,
                inModelUpdate: false,
                changeMode:null,
                trackedDependencies: {},
            }
        },
        computed: {
            objectVal: function() {
              return this.$store.getters.getMutaPropValue(this.objId,
                        this.propObject.id);
            },
            displayVal: function() {
              return this.displayValue(this.val);
            },
            selectItems: function () {
              return parseSelectData(
                  this.$store.getters.getDynamicValue(this.objId,
                    this.propObject.select));
            },
            hasSelect: function() {
                return !_.isEmpty(this.selectItems);
            },
            max_val: function () {
              return this.$store.getters.getDynamicValue(this.objId,
                        this.propObject.max_val)
            },
            min_val: function () {
                return this.$store.getters.getDynamicValue(this.objId,
                    this.propObject.min_val)
            },
            step: function () {
                return this.$store.getters.getDynamicValue(this.objId,
                    this.propObject.step)
            },
            read_only: function () {
                return this.$store.getters.getDynamicValue(this.objId,
                    this.propObject.read_only)
            },
            isChangeLabelVisible: function() {
                return (this.inUserChange || this.afterObjectChange);
            },
            validId : function() {
                return slugify(this.propObject.id);
            },
            labelClass: function() {
                var labelType = '';
                if (this.inUserChange) {
                    labelType = 'label-warning';
                }
                if (this.afterObjectChange) {
                    labelType = 'label-primary';

                    if ((this.changeMode == 'user') ||
                        (this.changeMode == 'master')) {
                        labelType = 'label-info';
                    }
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
            toggleSwitch: function() {
              if ((this.propObject.value_type === 'BOOL') &&
                  this.propObject.toggle) {
                  return $("input[type='checkbox']#" + this.validId);
              } else {
                return null;
              }
            }
        },
        watch: {
            uiVal: function(value, oldValue) {
                if (this.inObjectChange) {
                    this.inObjectChange = false;
                    this.afterObjectChange = true;
                } else if (!this.inUserChange) {
                    if (this.propObject.value_type == 'BOOL') {
                      this.labelVal = "Updating";
                    } else {
                      this.labelVal = this.displayValue(oldValue);
                    }
                    this.inUserChange = true;
                    this.afterObjectChange = false;
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
                    console.error(response)
                });
            },
            updateToggleSwitch: function() {
                if (this.toggleSwitch) {
                  this.toggleSwitch.prop('checked', this.uiVal);
                  this.toggleSwitch.data("bs.toggle").update(true);
                }
            },
            onUserChange: _.debounce(function() {
                // Update the value
                console.log("Updating object " + this.objId + " prop " +
                    this.propObject.id + " with value " + this.val);
                this.inModelUpdate = true;

                if (this.toggleSwitch) {
                    console.log(this.toggleSwitch.data("bs.toggle"));
                    this.toggleSwitch.data("bs.toggle")
                        .$toggleGroup.find("label")
                        .addClass("btn-danger");
                }

                var vm = this;
                this.$http.put('api/objects/' + encodeURIComponent(this.objId) +
                    '/props/' + encodeURIComponent(this.propObject.id) + '?value=' +
                    encodeURIComponent(this.uiVal)).then((response)=> {
                    vm.inUserChange = false;
                    vm.afterObjectChange = false;
                    vm.inModelUpdate = false;
                    if (this.toggleSwitch) {
                        this.toggleSwitch.data("bs.toggle")
                            .$toggleGroup.find("label")
                            .removeClass("btn-danger");
                    }
                    console.log("Updated object " + this.objId + " prop " +
                        this.propObject.id + " with value " + this.uiVal);
                },(response) => {
                    console.error(response);
                });
            }, 1000),
            onSelectClick: function() {
                this.afterObjectChange = false;
            },
            getSelectText: function(selectVal) {
                var temp = _.find(this.selectItems, ['value', selectVal]);
                return (temp)?temp.text:'Undefined';
            },
            displayValue: function(value) {
                if (this.toggleSwitch) {
                  return this.propObject.toggle[value?'on':'off'];
                } else if (this.hasSelect) {
                  return this.getSelectText(value);
                } else {
                  return value
                }
            },
        },
        created: function() {

          var vm = this;

          //Detect dynamic dependencies:
          this.trackedDependecies = {};
          this.trackedDependecies[this.propObject.id] = "value";
          _.forOwn(this.propObject, (value, key) => {
            if (isDynamic(value)) {
              vm.trackedDependecies[value.id] = key;
            }
          });

          //Subscribe to muta prop change events
          this.$store.subscribe((mutation, state) => {
            if ((mutation.type == 'muta_prop_change') &&
                ((mutation.payload.objId == vm.objId) ||
                (mutation.payload.objId ==
                            vm.$store.state.mutaObjects[vm.objId].class_id)) &&
                (_.has(vm.trackedDependecies, mutation.payload.propId))
                ) {

              // Let's process the changes...

              vm.changeMode = mutation.payload.eventSource;
//              console.log(vm.propObject.id + " changed " + vm.trackedDependecies[mutation.payload.propId] + " to " + mutation.payload.value);
              if (mutation.payload.propId == vm.propObject.id) {

                if (mutation.payload.value != this.uiVal) {
                    if (vm.inUserChange) {
                        //Don't change the value just the label
                        vm.labelVal = "Remote change to: " +
                            vm.displayValue(mutation.payload.value);
                        vm.afterObjectChange = true;
                    } else {
                        vm.labelVal = "Remote change from " +
                            vm.displayValue(vm.uiVal);
                        vm.inObjectChange = true;
                        vm.uiVal = mutation.payload.value;
                    }
                }

              } else if (vm.trackedDependecies[mutation.payload.propId]
                  != 'read_only') {
                  vm.labelVal = vm.trackedDependecies[mutation.payload.propId] +
                      ' changed';
                  vm.afterObjectChange = true;
              }
              vm.updateToggleSwitch(true); //Silent update
            }
          });

        },
        mounted: function () {
            // If we use toggle instead of checkbox, we have to manually service all stuff
            // that Vue is doing automatically by itself, because the way toggle is made,
            // it destroys all Vue bindings...
            if (this.toggleSwitch) {
                var self = this;
                var toggle = $("input[type='checkbox']#" + this.validId);
                toggle.bootstrapToggle( this.propObject.toggle );
                toggle.change(function () {
                    self.uiVal = toggle.prop('checked');
                    self.onUserChange();
                })

            }

        }
    }

</script>
