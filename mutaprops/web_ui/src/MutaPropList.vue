<template>
    <div id="muta-prop-list">
        <template v-if="displayType === 'actionsProps'">
        <!--<template v-if="true">-->
            <muta-prop-panel :prop-list="actionList" :obj-id="objId" heading="Actions">
            </muta-prop-panel>
            <muta-prop-panel :prop-list="propertyList" :obj-id="objId" heading="Properties">
            </muta-prop-panel>
        </template>
        <!--<template v-if="displayType === 'hierarchy'">-->
        <template v-if="true">
            <muta-prop-panel :prop-list="hierarchyList.otherActions" :obj-id="objId"
                             heading="Actions">

            </muta-prop-panel>
            <muta-prop-panel v-for="(panel, name) in hierarchyList.hierarchy" :prop-list="panel"
                             :obj-id="objId" :heading="name">
            </muta-prop-panel>
            <muta-prop-panel :prop-list="hierarchyList.otherProps" :obj-id="objId"
                             heading="Other Properties">

            </muta-prop-panel>
        </template>
    </div>
</template>

<script>
import Vue from 'vue';
import MutaPropPanel from './MutaPropPanel.vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export default {
    components: { MutaPropPanel },
    props: ['propList', 'objId', 'displayType'],
    data: function () {
      return {
        objectStore: null
      }
    },
    computed: {
        propertyList: function() {
            return this.propByType('property');
            },
        actionList: function() {
            return this.propByType('action');
        },
        hierarchyList: function() {
            let temp = {}
            temp.otherProps = []
            temp.otherActions = []
            temp.hierarchy = {}

            console.log("Computing like stupid!")

            for (let prop of this.propList) {
                if (prop.hierarchy != null) {
                    if (prop.hierarchy in temp.hierarchy) {
                        console.log("Adding a prop")
                        temp.hierarchy[prop.hierarchy].push(prop)
                    } else {
                        console.log("Creating a panel")
                        temp.hierarchy[prop.hierarchy] = [prop,]
                    }
                } else {
                    switch (prop.type) {
                        case 'property':
                            temp.otherProps.push(prop)
                            break
                        case 'action':
                            temp.otherActions.push(prop)
                            break
                    }
                }
            }
            console.log(temp)
            return temp
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
    },
    created: function () {
      this.objectStore = new Vuex.Store({
        state: {
          props: [],
          propVals: {},
        },
          mutations: {
            set_props (state, props) {
              state.props = props;
              //Update prop Vals
            }
          }
      });
    }
}
</script>

