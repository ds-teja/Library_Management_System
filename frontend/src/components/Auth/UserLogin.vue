<template>
    <div class="login-page">
      <router-link to="/" class="home-button" >Home</router-link>
      <div class="login-container">
        <h2>User Login</h2>
        <form @submit.prevent="login">
          <div class="form-group">
            <label for="username">Username</label>
            <input type="text" id="username" v-model="username" required>
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input type="password" id="password" v-model="password" required>
          </div>
          <button type="submit">Login</button>
        </form>
        <button class="register-button" @click="navigateToRegister">Register</button>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  export default {
    name: 'UserLogin',
    data() {
      return {
        errorMessage: '',
        username: '',
        password: ''
      }
    },
    methods: {
        async login() {
        try {
          const response = await axios.post('http://127.0.0.1:5000/api/auth/user-login', {
            username: this.username,
            email: this.email,
            password: this.password,
            age: this.age,
            nationality: this.nationality
          }, { withCredentials: true });

          this.$store.dispatch('login', { token: response.data.access_token });
          this.$router.push('/user-dashboard');
        } catch (error) {
          this.errorMessage = 'Invalid credentials! Please Try Again!';
          console.error(error);
        }
      },
      navigateToRegister() {
        this.$router.push('/user-register');
      }
    }
  }
  </script>
  
  <style scoped>
  .login-page {
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background: url('@/assets/homebackground.jpeg') no-repeat center center;
  background-size: cover;
  }
  
  .login-container {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    text-align: center;
  }
  
  .form-group {
    margin-bottom: 1rem;
  }
  
  input {
    width: 100%;
    padding: 0.5rem;
    margin-top: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
  
  button {
    padding: 0.5rem 1rem;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 1rem;
  }
  
  button:hover {
    background: #0056b3;
  }
  
  .register-button {
    background: #28a745;
    margin-top: 1rem;
  }
  
  .register-button:hover {
    background: #218838;
  }
  .home-button {
  position: absolute;
  top: 1rem;
  left: 1rem;
  padding: 0.5rem 1rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
}

.home-button:hover {
  background: #0056b3;
}


.error-message {
  color: red;
  margin-top: 1rem;
}
  </style>
  