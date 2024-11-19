<template>
  <div class="add-book-view">

  <div class="container"> <h1>Add New Section</h1>   
    <form @submit.prevent="addSection" class="form">
      <div class="form-group">
        <label for="name">Name:</label>
        <input type="text" v-model="newSection.name" id="name" required class="form-control">
      </div>
      <div class="form-group">
        <label for="description">Description:</label>
        <input type="text" v-model="newSection.description" id="description" required class="form-control">
      </div>
      <div class="form-group">
          <label for="cover">Upload Section Cover:</label>
          <input type="file" @change="handleCoverUpload" id="cover" class="form-control">
      </div>
      <button type="submit" class="btn btn-primary">Add Section</button>
    </form>

    <div v-if="isLoading" class="modal">
      <div class="modal-content">
        <p>Section is uploading, please wait...</p>
      </div>
    </div>
  </div>

  </div>
  
</template>

<script>
import axios from 'axios';

export default {
  name: 'AddSection',

  data() {
    return {
      isLoading: false,
      newSection: {
        name: '',
        description: '',
        created_date: '',
        cover: ''
      },
    }
  },

  methods: {
    async addSection() {
      try {
        this.isLoading = true;
        const formData = new FormData();
        formData.append('name', this.newSection.name);
        formData.append('description', this.newSection.description);
        formData.append('cover', this.newSection.cover);
        const access_token = localStorage.getItem('access_token')
        await axios.post('http://127.0.0.1:5000/api/sections', formData, {
          headers: {
            'Authorization': `Bearer ${access_token}`
          }
        });
        this.isLoading = false;
        alert("Section added successfully!");
        this.$router.push('/')
      } catch (error) {
        this.isLoading = false;
        alert('Error adding Section: ' + error.response.data.message +' Please Retry!');
        console.error('Error loading sections:', error);
      }
    },

    handleCoverUpload(event) {
      this.newSection.cover = event.target.files[0];
    },
  }
}
</script>

<style scoped>
.add-book-view{
  background: url('@/assets/genres.jpeg') no-repeat center center;
  padding:15px;
  height: 86vh;
  background-size: cover;
}
.container {
  max-width: 600px;
  margin: 100px auto;
  padding: 32px;
  background-color: #ffffff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

h1 {
  text-align: center;
  margin-bottom: 24px;
  font-size: 24px;
  color: #333333;
}

.form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 16px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #555555;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #cccccc;
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 14px;
}

.btn {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.btn:hover {
  background-color: #0056b3;
}

.modal {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  z-index: 1;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.5);
}

.modal-content {
  background-color: #ffffff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  font-size: 18px;
  color: #333333;
}
</style>
