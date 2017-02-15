<template>
<div :id="'mp-' + validId" class="panel panel-default panel-prop">
  <template v-if="propObject.value_type == 'HTML' ">
      <div class="panel-heading">{{ propObject.name }}</div>
      <div class="panel-body" v-html="htmlValue"></div>
  </template>
  <template v-else>
      <div class="panel-body">
          <form class="form-horizontal">
          <span class="pull-left control-label">
              <template v-if="propObject.doc">
              <a :href="'#' + validId" data-toggle="collapse">
              {{ propObject.name }}</a></template>
              <template v-else>{{ propObject.name }}</template>
          </span>
              <muta-prop-value :prop-object="propObject" :objId="objId">
              </muta-prop-value>
          </form>
          <div :id="validId" class="mutaprop-help collapse ">
              <hr>
              <div class="help-block" v-html="propObject.doc"></div>
              <!--<p> {{ doc }}</p>-->
          </div>
      </div>
  </template>
</div>
</template>

<script>
    import Vue from 'vue';
    import slugify from 'slugify';
    import MutaPropValue from './MutaPropValue.vue'
    export default {
        components: { MutaPropValue },
        props: ['propObject', 'objId'],
        data: function() {
            return {
                currentValue: this.propObject.value,
            }
        },
        computed: {
            validId : function() {
                return slugify(this.propObject.id).replace(/\_/g, "-");
            },
            doc: function () {
              return this.$store.getters.getDynamicValue(this.objId,
                        this.propObject.doc);
            },
            htmlValue: function() {
              return this.$store.getters.getMutaPropValue(this.objId,
                                                          this.propObject.id);
            }
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
