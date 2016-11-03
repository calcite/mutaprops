<template>
<div id="mutaprop" class="panel panel-default panel-prop">
  <div class="panel-body">
      <form class="form-horizontal">
          <span class="pull-left control-label">
              <template v-if="doc">
              <a :href="'#' + id" data-toggle="collapse">
              {{ name }}</a></template>
              <template v-else>{{ name }}</template>
          </span>
          <muta-prop-value v-bind="{ 'value': currentValue, 'type': type,
          'value_type': value_type, 'max_val': max_val, 'min_val': min_val,
           'step': step, 'read_only': read_only, 'id':id, 'objId': objId,
           'select': select}">
          </muta-prop-value>
      </form>
      <div :id="id" class="mutaprop-help collapse ">
          <hr>
          <p> {{ doc }}</p>
      </div>
  </div>
</div>
</template>

<script>
    import Vue from 'vue';
    import MutaPropValue from './MutaPropValue.vue'
    export default {
        components: { MutaPropValue },
        props: ['id', 'name', 'value', 'doc', 'type', 'max_val', 'value_type',
            'min_val', 'read_only', 'step', 'objId', 'select'],
        data: function() {
            return {
                currentValue: this.value,
            }
        },
    }
</script>

<style>
    .panel-prop {
        margin: 1em;
    }
    .mutaprop-help {
        margin-top: 3em;
    }
</style>
