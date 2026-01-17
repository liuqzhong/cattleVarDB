<template>
  <div id="app">
    <Navigation />
    <router-view />
  </div>
</template>

<script setup>
import Navigation from './components/Navigation.vue'
</script>

<style>
/* Global styles will be imported in main.js */
</style>
