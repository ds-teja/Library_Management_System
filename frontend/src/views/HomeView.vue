<template>
  <div class="home-view">
    <div class="content">
      <h1>A2Z Library</h1>
      <div class="login-options">
        <div class="option">
          <img src="@/assets/librarian.jpeg" alt="Librarian">
          <button @click="navigateToLibrarianLogin">Login as Librarian</button>
        </div>
        <div class="option">
          <img src="@/assets/users.jpeg" alt="User">
          <button @click="navigateToUserLogin">Login as User</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  methods: {
  navigateToLibrarianLogin() {
    this.$router.push({ name: 'LibrarianLogin' });
  },
  navigateToUserLogin() {
    this.$router.push({ name: 'UserLogin' });
  }
}
}
</script>

<style scoped>

.home-view {
  height: 97vh;
  background: url('@/assets/homebackground.jpeg') no-repeat center center;
  background-size: cover;
  display: flex;
  justify-content: center;
  align-items: center;
  margin:0;
  padding:0;
}

.content {
  text-align: center;
  color: white;
}

h1 {
  font-size: 3rem;
  margin-bottom: 2rem;
}

.login-options {
  display: flex;
  justify-content: space-around;
  width: 100%;
  max-width: 800px;
}

.option {
  text-align: center;
}

.option img {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 70%;
  padding:1px;
  background-color: antiquewhite;
}

.option button {
  display: block;
  margin: 1rem auto 0;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  cursor: pointer;
  border-radius:5px;
  border:2px antiquewhite;
}
</style>
