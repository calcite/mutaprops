<template>
<div id="mutaprop" class="panel panel-default">
  <div class="panel-body">
      <span><a :href="'#' + id" data-toggle="collapse">{{ name }}</a></span>
      <span class="pull-right">
      <muta-prop-value v-bind="{ 'value': value }"></muta-prop-value>
      </span>
      <div :id="id" class="collapse">
          <hr>
          <p> {{ doc }}</p>
      </div>
  </div>
</div>
</template>

<script>
    import MutaPropValue from './MutaPropValue.vue'
    export default {
        components: { MutaPropValue },
        props: ['id', 'name', 'value', 'doc', 'type', 'max_val', 'value_type',
            'min_val'],
    }
</script>