<template>

<div id="app">

<div id="header" class="navbar navbar-default navbar-fixed-top">
    <div class="navbar-header">
        <button class="navbar-toggle collapsed" type="button" data-toggle="collapse" data-target=".navbar-collapse">
            <i class="icon-reorder"></i>
        </button>
        <a class="navbar-brand" href="#">
            <span class="app-logo">&nbsp;</span>
            <span class="app-name">{{ appName }}</span>
            <span class="badge">{{ appStatus }}</span>
        </a>
    </div>
    <nav class="collapse navbar-collapse">
        <!--<ul class="nav navbar-nav">-->
            <!--<li class="dropdown">-->
              <!--<a href="#" class="dropdown-toggle" data-toggle="dropdown">File<b class="caret"></b></a>-->
                <!--<ul class="dropdown-menu">-->
                    <!--<li><a href="#">Load</a></li>-->
                    <!--<li><a href="#">Save</a></li>-->
                <!--</ul>-->
            <!--</li>-->
            <!--<li>-->
                <!--<a href="#">Remote</a>-->
            <!--</li>-->
        <!--</ul>-->
        <ul class="nav navbar-nav pull-right">
            <!--<li class="dropdown">-->
                <!--<a href="#" id="nbAcctDD" class="dropdown-toggle" data-toggle="dropdown"><i class="icon-user"></i>Help<i class="icon-sort-down"></i></a>-->
                <!--<ul class="dropdown-menu pull-right">-->
                    <!--<li><a href="#">Log Out</a></li>-->
                <!--</ul>-->
            <!--</li>-->
            <li>
                <a href="#" data-toggle="modal" data-target="#helpmodal">Help</a>
            </li>
        </ul>
    </nav>
</div>
    <router-view></router-view>
    <div class="log-drawer" v-bind:class="{ 'log-drawer-open': logDisplay }">
        <div class="log-lapel" v-on:click="toggleLogDisplay()">
            <span>Log</span><span class="badge badge-log">{{ unseenLogCount }}</span>
        </div>
        <div class="log-pane">
            <div class="log-controls form-inline">
                <button type="button" class="btn btn-default"
                        aria-label="Delete log" v-on:click="clearLogs()">
                   Clear
                </button>
                <div class="input-group">
                      <span class="input-group-addon" id="basic-addon1">
                          Filter
                      </span>
                      <input type="text" class="form-control"
                             placeholder="Level or text"
                             aria-describedby="basic-addon1"
                             v-model="logFilterString">
                    </div>
            </div>
            <div class="log-area" id="log-area">
               <ul class="log-list">
                   <li v-for="item in filteredLog"
                       v-bind:class="logStyle(item.levelname)">
                       {{ logItem(item) }}
                   </li>
               </ul>
            </div>
        </div>
    </div>
    <div class="modal fade helpmodal" tabindex="-1"
         role="dialog" aria-labelledby="helpmodal" aria-hidden="true" id="helpmodal">
        <div class="modal-dialog modal-lg" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal"
                            aria-label="Close">
                        <span aria-hidden="true">&times;</span></button>
                    <h4 class="modal-title" id="myModalLabel">Help</h4>
                </div>
                <div class="modal-body" v-html="helpDoc">
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>
</div><!-- app -->
</template>

<script>
import Vue from 'vue';
import SockJS from 'sockjs-client';
import _ from 'lodash';
import { vsprintf } from 'sprintf-js';
import { globalPropId } from './utils';

export default {
    data: function() {
        return {
            sock: null,
            appName: 'Connecting...',
            helpDoc: 'No help, sorry...',
            appStatus: '',
            logs: [],
            logFilterString: '',
            logDisplay: false,
            unseenLogs: 0
        }
    },
    computed: {
      filteredLog: function() {
          if (this.logFilterString !== '') {
              var filterString = this.logFilterString.toLowerCase();
              return _.filter(this.logs, function(o) {
                  return (_.includes(o.levelname.toLowerCase(), filterString) ||
                  _.includes(o.msg.toLowerCase(), filterString));
              });
          } else {
              return this.logs;
          }
      },
        unseenLogCount: function() {
            return (this.unseenLogs > 0) ? this.unseenLogs : '';
        }
    },
    methods: {
        sockjsSetup: _.throttle(function() {
            //Connect to notifications
            console.log("SockJS connecting");
            this.sock = new SockJS('/api/notifications/');
            var vm = this;
            this.sock.onopen = function(e) {
                console.log("Sockjs open");
                vm.appStatus = '';
            };
            this.sock.onmessage = function(e) {
                vm.processNotification(e.data);
            };
            this.sock.onclose = function(e) {
                console.log("SockJS closed - reconnecting.");
                vm.appStatus='Disconnected';
                vm.sockjsSetup();
            };
        }, 10000),

        processNotification: function(sockMsg) {
            var msg = sockMsg;
            console.log(JSON.stringify(msg));
            if (msg.type === "log") {
                //Check if we need to scroll down...
                let logArea = $('#log-area')[0]; //This might be assigned comp-wise
                let scrollDown = (logArea.scrollTop > (logArea.scrollHeight -
                                                        logArea.clientHeight -
                                                        30)); //30px snap margin

                // Scroll down the log view if necessary
                this.logs.push(msg.params);
                if (!this.logDisplay) {
                    this.unseenLogs++;
                }

                if (scrollDown) {
                    $('#log-area').scrollTop(logArea.scrollHeight);
                }

            } else if (msg.type == 'objects_change') {
                // Just reload all objects, vuex takes care of the rest.
                this.fetchObjects();
            } else if (msg.type == 'property_change') {
                // Deal with incoming property change notifications
                this.$store.commit('muta_prop_change', msg.params);
            } else {
                //TODO: Remove this if not necessary
                window.eventBus.$emit(msg.type, msg.params)
            }
        },

        fetchAppName: function() {
            var vm = this;
            this.$http.get('api/appname').then((response)=> {
                vm.appName = response.body;
                document.title = vm.appName;
            },(response) => {
                console.log(response)
            });
        },

        fetchHelpDoc: function() {
            var vm = this;
            this.$http.get('api/help').then((response)=> {
                vm.helpDoc = response.body;
            },(response) => {
                console.log(response)
            });
        },

        fetchObjects: function() {
            var vm = this;
            this.$http.get('api/objects').then((response)=> {
              console.log('Storing the muta Objects')
                vm.$store.commit('set_muta_objects', response.body);
            },(response) => {
                console.log(response)
            });
        },

        clearLogs: function () {
            for (let i = this.logs.length; i > 0; i--) {
                this.logs.pop();
            }
        },

        logStyle: function(loglevel) {
            return "loglevel-" + loglevel.toLowerCase();
        },

        logItem: function(item) {
            var timestamp = new Date(item.created * 1000);
            var time = timestamp.getHours() + ":" + timestamp.getMinutes() +
                ":" + timestamp.getSeconds() + "." +
                _.padStart(timestamp.getMilliseconds(), 3, '0');

            try {
                var formatted_msg = vsprintf(item.msg, item.args);
                return time + " [" + item.levelname + "] " + formatted_msg;
            }
            catch (e) {
                if (item.args.length == 0) {
                    var formatted_msg = vsprintf(item.msg.replace(/%/g, "%%"),
                        item.args);
                    return time + " [" + item.levelname + "] " + formatted_msg;
                } else {
                    console.error("Could not format log message: " + e)
                }
            }
        },

        toggleLogDisplay: function() {
          if (!this.logDisplay) {
              this.unseenLogs = 0;
          }
          this.logDisplay = !this.logDisplay;
        }
    },

    created: function() {
        this.fetchAppName();
        this.fetchHelpDoc();
        this.fetchObjects();
        this.sockjsSetup();
    }
}
</script>

<style>
:root {
    --drawerHeight: 307px;
}

#main {
    position: relative;
    height: 100%;
    overflow-y: auto;
    padding: 0 15px;
}

.log-drawer {
    position: fixed;
    bottom: 0;
    width: 100%;
    margin-bottom: calc( - var(--drawerHeight));
    transition: margin-bottom 0.3s ease-in-out;
}

.log-drawer-open {
    margin-bottom: 0px;
}

@media (max-width: 992px) {
    body {
        padding-top: 0px;
    }
}
@media (min-width: 992px) {
    #main-wrapper {
        float:right;
    }
}
@media (max-width: 992px) {
    #main-wrapper {
        padding-top: 0px;
    }
}
@media (max-width: 992px) {
    #sidebar-wrapper {
        position: static;
        height:auto;
        max-height: 300px;
  		border-right:0;
	}
}
@media(width <= 750px) {

    .log-drawer {
        position: fixed;
        bottom: 0;
        width: 100%;
        margin-bottom: calc( -(var(--drawerHeight) + 34) );
        transition: margin-bottom 0.3s ease-in-out;
    }

    .log-drawer-open {
        margin-bottom: 0px;
    }
}
</style>
