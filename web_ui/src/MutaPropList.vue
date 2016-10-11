<template>
    <div id="muta-prop-list">
        <muta-prop v-for="mutaprop in propList" v-bind="mutaprop"></muta-prop>
    </div>
</template>

<script>
import MutaProp from './MutaProp.vue'

export default {
    components: { MutaProp },
    props: ['propList']
}
</script>