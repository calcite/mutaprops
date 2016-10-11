<template>
<div id="mutaprop" class="panel panel-default">
  <div class="panel-body">
      <span><a :href="'#' + id" data-toggle="collapse">{{ name }}</a></span>
      <span class="pull-right"><input v-model="value"></span>
      <div :id="id" class="collapse">
          <hr>
          <p> {{ doc }}</p>
      </div>
  </div>
</div>
</template>

<script>
    export default {
        props: ['id', 'name', 'value', 'doc'],
//        data () {
//            return {
//                propName: 'Name of the property',
//                propValue: 'A value like no other'
//            }
//        }
    }
</script>