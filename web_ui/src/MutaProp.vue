<template>
    <div id="mutaprop">
        <span>{{ propName }}</span>
        <span>{{ propValue }}</span>
        <p>Jeste neco</p>
        <alert type="success">Povedlo se.</alert>
    </div>
</template>

<script>
    export default {
        data () {
            return {
                propName: 'Name of the property',
                propValue: 'A value like no other'
            }
        }
    }
</script>