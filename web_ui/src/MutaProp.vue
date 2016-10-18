<template>
<div id="mutaprop" class="panel panel-default panel-prop">
  <div class="panel-body">
      <span><a :href="'#' + id" data-toggle="collapse">{{ name }}</a></span>
      <muta-prop-value v-bind="{ 'value': currentValue, 'type': type,
      'value_type': value_type, 'max_val': max_val, 'min_val': min_val,
       'step': step, 'read_only': read_only, 'id':id, 'objId': objId}"
      v-on:valuechanged="updateProp">
      </muta-prop-value>
      <div :id="id" class="collapse">
          <hr>
          <p> {{ doc }}</p>
      </div>
  </div>
</div>
</template>

<script>
    import Vue from 'vue';
    import Resource from 'vue-resource';
    Vue.use(Resource);
    import MutaPropValue from './MutaPropValue.vue'
    export default {
        components: { MutaPropValue },
        props: ['id', 'name', 'value', 'doc', 'type', 'max_val', 'value_type',
            'min_val', 'read_only', 'step', 'objId'],
        data: function() {
            return {
                currentValue: this.value,
            }
        },
        methods: {
            updateProp: function(objectId, propertyId, value) {
                console.log("updateProp called id:" + objectId + " value:" + value);
                var vm = this;
                this.$http.put('api/objects/' + objectId + '/props/'
                        + propertyId + '?value=' + value).then((response)=> {
                    vm.currentValue = value
                },(response) => {
                    console.log(response)
                });
            }
        }
    }
</script>

<style>
    .panel-prop {
        margin: 1em;
    }
</style>
