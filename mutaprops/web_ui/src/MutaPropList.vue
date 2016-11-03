<template>
    <div id="muta-prop-list">
        <div class="panel panel-default panel-proplist">
            <div class="panel-heading">Actions</div>
            <muta-prop v-for="mutaprop in actionList" v-bind="mutaprop"
                       :obj-id="objId"></muta-prop>
        </div>
        <div class="panel panel-default panel-proplist">
            <div class="panel-heading">Properties</div>
            <muta-prop v-for="mutaprop in propertyList" v-bind="mutaprop"
            :obj-id="objId"></muta-prop>
        </div>
    </div>
</template>

<script>
import MutaProp from './MutaProp.vue'

export default {
    components: { MutaProp },
    props: ['propList', 'objId'],
    computed: {
        propertyList: function() {
            return this.propByType('property');
            },
        actionList: function() {
            return this.propByType('action');
        }
    },
    methods: {
        propByType: function(type) {
            let temp = [];
            for (let prop of this.propList) {
                if (prop.type == type) {
                    temp.push(prop);
                }
            }
            return temp;
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