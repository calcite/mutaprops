<template>
<div id="mutaprop" class="panel panel-default">
  <div class="panel-body">
      <span><a href="#prop-desc" data-toggle="collapse">{{ name }}</a></span>
      <span class="pull-right"><input v-model="value"></span>
      <div id="prop-desc" class="collapse">
          <hr>
          <p> {{ description }}</p>
      </div>
  </div>
</div>
</template>

<script>
    export default {
        props: ['name', 'value', 'description'],
//        data () {
//            return {
//                propName: 'Name of the property',
//                propValue: 'A value like no other'
//            }
//        }
    }
</script>