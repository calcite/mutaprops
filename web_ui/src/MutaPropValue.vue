<template>
    <span class="pull-right">
        <span class="label label-warning" v-if="valueChanged">{{ value }}</span>
        <template v-if="hasSelect">
            <select  :disabled="read_only" class="form-control" v-model="val">
                <option v-for="option in selectValues"
                        v-bind:value="option.value">
                    {{ option.text }}
                </option>
            </select>
        </template>
        <template v-else>
            <input v-if="(value_type == 'INT') || (value_type == 'REAL')"
                   v-model.number.lazy="val" type="number"
                   :min="min_val" :max="max_val" :step="step"
                   :disabled="read_only" class="form-control">
            <input v-if="value_type == 'BOOL'" type="checkbox" v-model="val"
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
    import _ from 'lodash';
    import BiMap from 'bimap';

    export default {
        props: ['max_val', 'value_type', 'min_val', 'value', 'type', 'step',
            'read_only', 'id', 'objId', 'select'],
        data: function() {
            return {
                val: this.value,
                selectMap: null,
            }
        },
        computed: {
            valueChanged: function() {
                return this.value != this.val;
            },
            hasSelect: function() {
                return !_.isEmpty(this.select);
            },
            selectValues: function() {
                var temp = [];
                for (let item of this.select) {
                    temp.push({ text: item[0], value: item[1]})
                }
                return temp;
            },
        },
        watch: {
            val: _.debounce(function(value, oldValue) {
                console.log('Value changed.');
                this.$emit('valuechanged', this.objId, this.id, this.val);
            }, 1000),
            select: function() {
                updateSelectMap();
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
            }
        }
    }

</script>