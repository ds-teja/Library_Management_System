<template>
    <div class="user-table">
      <h1>User Management</h1>
      <table>
        <thead>
          <tr>
            <th>Username</th>
            <th>Email</th>
            <th>Nationality</th>
            <th>Created Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.nationality }}</td>
            <td>{{ formatDate(user.created_date) }}</td>
            <td>
              <button @click="viewProfile(user.id)" class="action-button">View Profile</button>
              <button @click="viewActivityLog(user.id)" class="action-button">View Requests</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    name: 'UserTable',
    data() {
      return {
        users: []
      };
    },
    mounted() {
      this.loadUsers();
    },
    methods: {
      async loadUsers() {
        try {
          const access_token = localStorage.getItem('access_token');
          const response = await axios.get('http://127.0.0.1:5000/api/users',{
            headers:{
              'Authorization':`Bearer ${access_token}`
            }
          });
          this.users = response.data;
        } catch (error) {
          console.error('Error fetching users:', error);
        }
      },
      formatDate(date) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return new Date(date).toLocaleDateString(undefined, options);
      },
      viewProfile(userId) {
       this.$router.push(`/users/stats/${userId}`);
      },
      viewActivityLog(userId) {
       this.$router.push(`/librarian-dashboard/users/requests/${userId}`);
      },
    }
  };
  </script>
  
  <style scoped>
  .user-table {
    font-family: 'Arial', sans-serif;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }
  
  h1 {
    text-align: center;
    margin-bottom: 20px;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
  }
  
  th, td {
    padding: 10px;
    border: 1px solid #ddd;
  }
  
  th {
    background-color: #f4f4f4;
  }
  
  .action-button {
    margin: 5px;
    padding: 8px 12px;
    background-color: #007BFF;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .action-button:hover {
    background-color: #0056b3;
  }
  </style>
  