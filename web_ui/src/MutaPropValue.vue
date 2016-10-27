<template>
    <span class="pull-right form-inline">
        <label :class="labelClass" v-if="isChangeLabelVisible">
            {{ labelVal }}
        </label>
        <template v-if="hasSelect">
            <select  :disabled="read_only" class="form-control" v-model="val"
            :class="inputClass" v-on:change="onUserChange">
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
                   v-on:change="onUserChange">
            <input v-if="value_type == 'BOOL'" type="checkbox" v-model="val"
                   :class="inputClass" v-on:change="onUserChange"
                   :disabled="read_only">
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
                afterObjectChange: false,
                selectItems: [],
            }
        },
        computed: {
            isChangeLabelVisible: function() {
                return (this.inUserChange || this.afterObjectChange);
//                return this.value != this.val;
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
                if (this.afterObjectChange) {
                    labelType = 'label-primary';
                }
                return ['label', labelType];
            },
            inputClass: function() {
                return this.inUserChange?'unset-value':'';
            },
        },
        watch: {
            val: function(value, oldValue) {
                if (this.inObjectChange) {
//                    console.log("Edited by object change")
                    this.inObjectChange = false;
                    this.afterObjectChange = true;
                } else {
                    if (!this.inUserChange) {
                        this.labelVal = this.displayValue(oldValue);
                        this.inUserChange = true;
                        this.afterObjectChange = false;
                    }
//                    console.log("inUserChange")
                }
//                console.log("UserChange: " + this.inUserChange);
//                console.log("AfterObjectChange " + this.afterObjectChange);
//                _.debounce(function(value, oldValue) {
//                    console.log('Value changed.');
//                    this.inUserChange = true;
//                    this.$emit('valuechanged', this.objId, this.id, this.val);
//                }, 1000);
            }
        },
        methods: {
            actionExecuted: function() {
                var vm = this;
                this.$http.put('api/objects/' + this.objId + '/props/'
                        + this.id + '/action').then((response)=> {
                    console.log("Action executed object:" + this.objId +
                            " action:" + this.id);
                },(response) => {
                    console.log(response)
                });
            },
            onUserChange: _.debounce(function() {
//                console.log("User change finished.");
                // Update the value
                console.log(this.inUserChange);
                console.log(this.val);
//                this.updateValue();
                console.log("Updating object");
                var vm = this;
                this.$http.put('api/objects/' + this.objId + '/props/'
                        + this.id + '?value=' + this.val).then((response)=> {
//                    vm.currentValue = value
                    vm.inUserChange = false;
                    vm.afterObjectChange = false;
                    console.log("Value update in object.");
                },(response) => {
                    console.log(response);
                });
            }, 1000),
            updateSelectItems: function(selectData) {
                this.selectItems = [];
                for (let item of this.select) {
                    this.selectItems.push({ text: item[0], value: item[1]})
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

                this.updateSelectItems(this.select);
            }

            //Prepare notification processing
            var vm = this;
            window.eventBus.$on('property_change', function(params) {
                if ((params.objId == vm.objId) && (params.propId == vm.id)) {
                    vm.inObjectChange = true;
                    if (vm.inUserChange) {
                        //Don't change the value just the label
                        vm.labelVal = vm.displayValue(params.value);
                        vm.afterObjectChange = true;
                    } else {
//                        console.log("Not is user change.");
                        vm.labelVal = vm.displayValue(vm.val);
                        vm.val = params.value;
                    }
                }
            });
        }
    }

</script>

<style>
    .unset-value {
        background-color: rgba(240,173,78, 0.3);
    }
</style>