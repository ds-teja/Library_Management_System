<template>
  <div id="app">
    <div v-if="isAuthenticated">
      <div v-if="userRole=='librarian'">
        <div class="navbar">
          <router-link to="/" class="home-link">Librarian Dashboard</router-link>
          <div class="nav-links">
            <router-link to="/librarian-dashboard" class="nav-link"><strong>All Sections</strong></router-link>
            <router-link to="/librarian-dashboard/allbooks" class="nav-link"><strong>All Books</strong></router-link>
            <router-link to="/librarian-dashboard/requests" class="nav-link"><strong>Handle Requests</strong></router-link>
            <router-link to="/librarian-dashboard/users" class="nav-link"><strong>Handle Users</strong></router-link>
            <router-link to="/librarian-dashboard/stats" class="nav-link"><strong>Stats</strong></router-link>
            <button @click="logout" class="nav-link"><strong>Logout</strong></button>
          </div>
        </div>
      </div>
      <div v-if="userRole=='user'">
        <div class="navbar">
            <router-link to="/" class="home-link">User Dashboard</router-link>
            <div class="nav-links">
              <router-link to='/user-dashboard/requests' class="nav-link"><strong>My Requests</strong></router-link>
              <router-link to='/user-dashboard' class="nav-link"><strong>All Books</strong></router-link>
              <router-link to='/user-dashboard/sections' class="nav-link"><strong>All Sections</strong></router-link>
              <router-link to='/user-dashboard/bookshelves' class="nav-link"><strong>My Bookshelves</strong></router-link>
              <router-link to='/users/stats' class="nav-link"><strong>My Profile</strong></router-link>
              <button @click="logout" class="nav-link"><strong>Logout</strong></button>
            </div>
        </div>
      </div>
    </div>
    <div style="margin-top:0.5em">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import {mapActions,mapGetters} from 'vuex';
export default {
  name: 'App',

  computed: {
    ...mapGetters(['isAuthenticated','userRole']),
  },

  methods:{
    ...mapActions(['logout']),
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  display: flex;
  gap:50px;
  flex-direction: column;
}


.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 30px;
    background-color: #2c3e50;
    color: white;
    position:fixed;
    top: 0;
    left:0;
    width: 97%;
}

.home-link {
    font-size: 24px;
    font-weight: bold;
    color: #ecf0f1;
    text-decoration: none;
}

.nav-links {
    display: flex;
    gap: 10px;
}

.nav-link {
    color: #ecf0f1;
    text-decoration: none;
    padding: 8px 16px;
    background-color: #3498db;
    border-radius: 5px;
    border:none;
    transition: background-color 0.3s;
    cursor:pointer;
    margin-right:10px;
}

.nav-link:hover {
    background-color: #2980b9;
}

</style>
