<template>
    <div v-if="hasContent" class="panel panel-default panel-proplist">
        <div class="panel-heading">
            <a data-toggle="collapse" :href="'#' + collapseName">
                {{ heading }}</a>
        </div>
        <div :id="collapseName" class="panel-collapse collapse in">
            <muta-prop v-for="mutaprop in propList" v-bind="mutaprop"
                       :obj-id="objId"></muta-prop>
        </div>
    </div>
</template>
<script>
import _ from 'lodash'
import slug from 'slug'
import MutaProp from './MutaProp.vue'
export default {
    components: { MutaProp },
    props: ['propList', 'objId', 'heading'],
    computed: {
        hasContent: function() {
            return !(_.isEmpty(this.propList))
        },
        collapseName: function() {
            return slug(this.heading) + '-collapse'
        }
    }
}
</script>

<style>
    .panel-proplist {
        border-color: #949494;
    }
    .panel-proplist>.panel-heading {
        background-color: #949494;
        color: #ffffff;
    }
</style>
