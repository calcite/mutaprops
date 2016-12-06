<template>
    <span class="pull-right form-inline">
        <label :class="labelClass" v-if="isChangeLabelVisible">
            {{ labelVal }}
        </label>
        <template v-if="hasSelect">
            <select  :disabled="read_only" class="form-control" v-model="val"
            :class="inputClass" v-on:change="onUserChange"
                     v-on:click="onSelectClick">
                <option v-for="option in selectItems"
                        v-bind:value="option.value">
                    {{ option.text }}
                </option>
            </select>
        </template>
        <template v-else>
            <input v-if="(value_type == 'INT') || (value_type == 'REAL')"
                   v-model.number="val" type="number"
                   :min="min_val" :max="max_val" :step="step"
                   :disabled="read_only" class="form-control"
                   :class="inputClass"
                   v-on:change="onUserChange" v-on:keyup.enter="onUserChange">
            <input v-if="value_type == 'BOOL'" type="checkbox" data-toggle="toggle"
                   v-model="val" :class="inputClass" v-on:change="onUserChange"
                   :disabled="read_only" :id="id">
            <input v-if="value_type == 'STRING'" v-model="val" type="text"
                   :class="inputClass" :disabled="read_only"
                   :maxlength="max_val" class="form-control"
                   v-on:change="onUserChange" v-on:keyup.enter="onUserChange">
            <button v-if="type == 'action'" v-on:click="actionExecuted"
                    type="button"
                    class="btn btn-primary">
                Action
            </button>
        </template>
    </span>
</template>

<script>
    import Vue from 'vue';
    import _ from 'lodash';
    import Resource from 'vue-resource';
    Vue.use(Resource);

    export default {
        props: ['max_val', 'value_type', 'min_val', 'value', 'type', 'step',
            'read_only', 'id', 'objId', 'select'],
        data: function() {
            return {
                val: this.value,
                labelVal: this.value,
                inUserChange: false,
                inObjectChange: false,
                afterSelectUpdate: false,
                afterObjectChange: false,
                inModelUpdate: false,
                selectItems: [],
                dynamicSelectId: null,
                dynamicSelectClassId: null,
                changeMode:null,
            }
        },
        computed: {
            isChangeLabelVisible: function() {
                return (this.inUserChange || this.afterObjectChange ||
                this.afterSelectUpdate);
            },
            hasSelect: function() {
                return !_.isEmpty(this.select);
            },
            selectValues: function() {
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
                return ['label', labelType];
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
                        '/props/' + encodeURIComponent(this.id) + '/action')
                        .then((response)=> {
                    console.log("Action executed object:" + this.objId +
                            " action:" + this.id);
                },(response) => {
                    console.log(response)
                });
            },
            onUserChange: _.debounce(function() {
                // Update the value
                console.log("Updating object " + this.objId + " prop " +
                        this.id + " with value " + this.val);
                this.afterSelectUpdate = false;
                this.inModelUpdate = true;
                var vm = this;
                this.$http.put('api/objects/' + encodeURIComponent(this.objId) +
                        '/props/' + encodeURIComponent(this.id) + '?value=' +
                        encodeURIComponent(this.val)).then((response)=> {
                    vm.inUserChange = false;
                    vm.afterObjectChange = false;
                    vm.inModelUpdate = false;
                    console.log("Updated object " + this.objId + " prop " +
                            this.id + " with value " + this.val);
                },(response) => {
                    console.log(response);
                });
            }, 1000),
            onSelectClick: function() {
                this.afterSelectUpdate = false;
            },
            initSelect: function(selectObj) {
                if (selectObj.source == 'dynamic') {
                    this.dynamicSelectId = selectObj.id;
                    if ('classId' in selectObj) {
                        this.dynamicSelectClassId = selectObj.classId;
                    }
                }

                this.updateSelectItems(selectObj.data);
            },
            updateSelectItems: function(selectData) {
                this.selectItems = [];
                if (selectData.type == 'map') {
                    for (let item of selectData.items) {
                        this.selectItems.push({ text: item[0], value: item[1]})
                    }
                } else if (selectData.type == 'list') {
                    for (let item of selectData.items) {
                        this.selectItems.push({ text: item, value: item})
                    }
                }
            },
            getSelectText: function(selectVal) {
                var temp = _.find(this.selectItems, ['value', selectVal]);
                return (temp)?temp.text:'Undefined';
            },
            displayValue: function(value) {
                return this.hasSelect?this.getSelectText(value):value;
            }
        },
        created: function() {
            //update select values
            if (this.hasSelect) {
                this.initSelect(this.select);
            }

            //Prepare notification processing
            var vm = this;
            window.eventBus.$on('property_change', function(params) {
                if ((params.objId == vm.objId) && (params.propId == vm.id)) {
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
                        vm.val = params.value;
                    }
                }
            });
            if (this.dynamicSelectId != null) {
                window.eventBus.$on('select_change', function(params) {
                    var temp_id;
                    if (vm.dynamicSelectClassId != null) {
                       temp_id = vm.dynamicSelectClassId;
                    } else {
                        temp_id = vm.objId;
                    }

                    if ((params.objId == temp_id) &&
                            (params.selectId == vm.dynamicSelectId)) {
                        vm.updateSelectItems(params.value);
                        vm.labelVal = "Selection Updated";
                        vm.afterSelectUpdate = true;
                    }
                });
            }
        },
        mounted: function () {
            // If we use toggle instead of checkbox, we have to manually service all stuff
            // that Vue is doing automatically by itself, because the way toggle is made,
            // it destroys all Vue bindings...
            if (this.value_type === 'BOOL') {
                var self = this;
                var toggle = $("input[type='checkbox']#" + this.id);
                toggle.bootstrapToggle();
                toggle.change(function () {
                    console.log("Checkbox changed");
                    self.val = toggle.prop('checked');
                    self.onUserChange();
//                    console.log(toggle.prop('checked'));
                    //TODO: check why is it registering as remoteChange and not userChange
                    //TODO: add automatic update on remote change
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
</style>
