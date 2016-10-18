<template>
    <span class="pull-right">
        <span class="label label-warning" v-if="valueChanged">{{ value }}</span>
    <input v-if="(value_type == 'INT') || (value_type == 'REAL')" v-model.number.lazy="val" type="number"
           :min="min_val" :max="max_val" :step="step" :disabled="read_only">
    <input v-if="value_type == 'BOOL'" type="checkbox" v-model="val"
           :disabled="read_only">
        <button v-if="type == 'action'" v-on:click="actionExecuted">
            Action
        </button>
    </span>
</template>

<script>
    import _ from 'lodash';
    export default {
        props: ['max_val', 'value_type', 'min_val', 'value', 'type', 'step',
            'read_only', 'id', 'objId'],
        data: function() {
            return {
                val: this.value
            }
        },
        computed: {
            valueChanged: function() {
                return this.value != this.val;
            }
        },
        watch: {
            val: _.debounce(function(value, oldValue) {
                console.log('Value changed.');
                this.$emit('valuechanged', this.objId, this.id, this.val);
            }, 1000)
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