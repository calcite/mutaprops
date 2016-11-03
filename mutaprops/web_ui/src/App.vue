<template>

<div id="app">

<div id="header" class="navbar navbar-default navbar-fixed-top">
    <div class="navbar-header">
        <button class="navbar-toggle collapsed" type="button" data-toggle="collapse" data-target=".navbar-collapse">
            <i class="icon-reorder"></i>
        </button>
        <a class="navbar-brand" href="#">
           {{ appName }}
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
                <div class="modal-body">
                    Here should be help.
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

export default {
    data: function() {
        return {
            sock: null,
            appName: 'Connecting...',
            appStatus: '',
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
            var msg = JSON.parse(sockMsg);
            console.log(msg);
            window.eventBus.$emit(msg.type, msg.params);
        },

        fetchAppName: function() {
            var vm = this;
            this.$http.get('api/appname').then((response)=> {
                vm.appName = response.body;
            },(response) => {
                console.log(response)
            });
        },

    },

    created: function() {
        this.fetchAppName();
        this.sockjsSetup();
    }
}
</script>

<style>
body {
    font-family: Helvetica, sans-serif;
    padding-top: 50px;
    overflow: hidden;
}

.navbar-default {
    background-color: #003394;
}
.navbar-default .navbar-brand {
    color: #ffffff;
}

.navbar-default .navbar-nav>li>a {
    color: #ffffff;
}

.navbar-header a.navbar-brand:hover,.navbar-header a.navbar-brand:focus {
    /*background-color: #FFFF00;*/
    color: #FFC0CB;
}
.navbar-default .navbar-nav> li > a:hover, .navbar-default .navbar-nav > li > a:focus {
    /*background-color: #FFFF00;*/
    color: #FFC0CB;
}

.navbar {
    border: 0px;
    -webkit-box-shadow: 0 8px 6px -6px #999;
    -moz-box-shadow: 0 8px 6px -6px #999;
    box-shadow: 0 8px 6px -6px #999;

    /* the rest of your styling */
}
#main {
    position: relative;
    height: 100%;
    overflow-y: auto;
    padding: 0 15px;
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
</style>
