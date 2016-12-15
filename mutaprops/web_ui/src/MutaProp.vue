<template>
<div :id="'mp-' + validId" class="panel panel-default panel-prop">
  <div class="panel-body">
      <form class="form-horizontal">
          <span class="pull-left control-label">
              <template v-if="doc">
              <a :href="'#' + validId" data-toggle="collapse">
              {{ name }}</a></template>
              <template v-else>{{ name }}</template>
          </span>
          <muta-prop-value v-bind="{ 'value': currentValue, 'type': type,
          'value_type': value_type, 'max_val': max_val, 'min_val': min_val,
           'step': step, 'read_only': read_only, 'id':id, 'objId': objId,
           'select': select, 'toggle': toggle }">
          </muta-prop-value>
      </form>
      <div :id="validId" class="mutaprop-help collapse ">
          <hr>
          <div class="help-block" v-html="doc"></div>
          <!--<p> {{ doc }}</p>-->
      </div>
  </div>
</div>
</template>

<script>
    import Vue from 'vue';
    import slugify from 'slugify';
    import MutaPropValue from './MutaPropValue.vue'
    export default {
        components: { MutaPropValue },
        props: ['id', 'name', 'value', 'doc', 'type', 'max_val', 'value_type',
            'min_val', 'read_only', 'step', 'objId', 'select', 'toggle'],
        data: function() {
            return {
                currentValue: this.value,
            }
        },
        computed: {
            validId : function() {
                return slugify(this.id).replace(/\_/g, "-");
            },
        }
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
