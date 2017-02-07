<template>
    <div v-if="hasContent" class="panel panel-default panel-proplist">
        <div class="panel-heading">
            <a data-toggle="collapse" :href="'#' + collapseName">
                {{ heading }}</a>
        </div>
        <div :id="collapseName" class="panel-collapse collapse in">
            <muta-prop v-for="mutaprop in propList" :prop-object="mutaprop"
                       :obj-id="objId"></muta-prop>
        </div>
    </div>
</template>
<script>
import _ from 'lodash'
import slugify from 'slugify'
import MutaProp from './MutaProp.vue'
export default {
    components: { MutaProp },
    props: ['propList', 'objId', 'heading'],
    computed: {
        hasContent: function() {
            return !(_.isEmpty(this.propList));
        },
        collapseName: function() {
            return slugify(this.heading) + '-collapse';
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

    .panel-heading>a {
        color: #ffffff;
    }
</style>
