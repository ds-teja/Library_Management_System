<template>
    <div>
      <h1>OOPS! The page you are tyring to search does not exist!</h1>
      <div>
        <button @click="goBack">Go Back</button>
      </div>
    </div>
</template>
  
<script>
export default {
  name: 'UserDashboard',
  methods: {
    goBack() {
      this.$router.go(-1);
    },
  }
};
</script>

<style scoped>
/* No global styles affecting the layout */
</style>
  