<template>

<div id="app">

<div id="header" class="navbar navbar-default navbar-fixed-top">
    <div class="navbar-header">
        <button class="navbar-toggle collapsed" type="button" data-toggle="collapse" data-target=".navbar-collapse">
            <i class="icon-reorder"></i>
        </button>
        <a class="navbar-brand" href="#">
           ConCon
        </a>
    </div>
    <nav class="collapse navbar-collapse">
        <ul class="nav navbar-nav">
            <li class="dropdown">
              <a href="#" class="dropdown-toggle" data-toggle="dropdown">File<b class="caret"></b></a>
                <ul class="dropdown-menu">
                    <li><a href="#">Load</a></li>
                    <li><a href="#">Save</a></li>
                </ul>
            </li>
            <li>
                <a href="#">Remote</a>
            </li>
        </ul>
        <ul class="nav navbar-nav pull-right">
            <li class="dropdown">
                <a href="#" id="nbAcctDD" class="dropdown-toggle" data-toggle="dropdown"><i class="icon-user"></i>Help<i class="icon-sort-down"></i></a>
                <ul class="dropdown-menu pull-right">
                    <li><a href="#">Log Out</a></li>
                </ul>
            </li>
        </ul>
    </nav>
</div>
    <router-view></router-view>
</div><!-- app -->
</template>

<script>
import Vue from 'vue';

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

.navbar {
    border: 0px;
    -webkit-box-shadow: 0 8px 6px -6px #999;
    -moz-box-shadow: 0 8px 6px -6px #999;
    box-shadow: 0 8px 6px -6px #999;

    /* the rest of your styling */
}
#wrapper {
    min-height: 100%;
    height: 100%;
    width: 100%;
    position: absolute;
    top: 0px;
    left: 0;
    display: inline-block;
}
#main-wrapper {
    height: 100%;
    overflow-y: auto;
    padding: 50px 0 0px 0;
}
#main {
    position: relative;
    height: 100%;
    overflow-y: auto;
    padding: 0 15px;
}
#sidebar-wrapper {
    height: 100%;
    padding: 50px 0 0px 0;
    position: fixed;
    border-right: 1px solid gray;
}
#sidebar {
    position: relative;
    height: 100%;
    overflow-y: auto;
}
#sidebar .list-group-item {
        border-radius: 0;
        border-left: 0;
        border-right: 0;
        border-top: 0;
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
