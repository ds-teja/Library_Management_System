<template>
  <LibrarianAllSections></LibrarianAllSections>
</template>

  
<script>
import LibrarianAllSections from '../components/Section/LibrarianAllSections.vue'
import {mapActions} from 'vuex';
export default {
  name: 'LibrarianDashboard',  

  components:{
    LibrarianAllSections,
  },

  methods:{
    ...mapActions(['logout']),
  }
}
</script>

<style scoped>
</style>

  