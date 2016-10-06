<template>
  <div id="app">
    <img src="./assets/logo.png">
    <h1>{{ msg }}</h1>
    <muta-prop></muta-prop>
  </div>
</template>

<script>
import MutaProp from './MutaProp.vue'

export default {
  components: { MutaProp },
  data () {
    return {
      msg: 'Hello Vue!'
    }
  }
}
</script>

<style>
body {
  font-family: Helvetica, sans-serif;
}
</style>
