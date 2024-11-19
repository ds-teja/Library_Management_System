<template>
    <div>
      <UserAllBooks></UserAllBooks>
    </div>
</template>
  
<script>
import {mapActions} from 'vuex';
import UserAllBooks from '../components/Book/UserAllBooks.vue'

export default {
  name: 'UserDashboard',

  components: {
    UserAllBooks,
  },

  methods: {
    ...mapActions(['logout']),
  }
}
</script>
  
<style scoped>
/* Add styles if necessary */
</style>
