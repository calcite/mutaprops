<template>
    <div id="sidebar-wrapper" class="col-xs-12 col-md-2">
        <div id="sidebar">
            <ul class="nav list-group">
                <li v-for="mutaObj in objectList">
                    <router-link :to="{ name: 'object', params: {id: mutaObj}}"
                    v-bind:class="['list-group-item',
                     (mutaObj == selectedObject)?'sidebar-selected':'']">
                       {{ mutaObj }}
                    </router-link>
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
import Resource from 'vue-resource';
import Vue from 'vue';
Vue.use(Resource);


export default {
    props: ['objectList', 'selectedObject'],
}
</script>

