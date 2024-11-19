<template>
  <div v-if="idExists">
    <div class="addbook-view"> 
        <div class="add-book-container">
            <div v-if="this.id==null">
              <h1 class="form-title">Add New Book in any Section</h1>
            </div>
            <div v-else>
              <h1 class="form-title">Add New Book in {{ sectionName }} Section</h1>
            </div>
            
            <form @submit.prevent="addBook" class="add-book-form">
            <div class="form-group">
                <label for="name">Name:</label>
                <input type="text" v-model="newBook.name" id="name" required>
            </div>
            <div class="form-group">
                <label for="author">Author:</label>
                <input type="text" v-model="newBook.author" id="author" required>
            </div>
            <div class="form-group">
                <label for="cover">Upload Book Cover:</label>
                <input type="file" @change="handleCoverUpload" id="cover">
            </div>
            <div class="form-group">
                <label for="file">Upload Book Content:</label>
                <input type="file" @change="handleFileUpload" id="file" required>
            </div>
            <div class="form-group">
                <label for="num_pages">Number of Pages:</label>
                <input type="number" v-model="newBook.num_pages" id="num_pages" required>
            </div>
            <div v-if="id==null" class="form-group">
              <select v-model="newSectionId">
                <option value="" disabled selected>Select any Section</option>
                <option v-for="section in sectionlist" :key="section.id" :value="section.id">{{ section.name }}</option>
              </select>
            </div>
            <div class="form-group">
                <label for="prologue">Prologue:</label>
                <textarea v-model="newBook.prologue" id="prologue" required></textarea>
            </div>
            <button type="submit" class="submit-button">Add Book</button>
            </form>
        </div>
    </div>

    <div v-if="isLoading" class="modal">
      <div class="modal-content">
        <p>Book is uploading, please wait...</p>
      </div>
    </div>
  </div>   
  <div v-else>
    <div v-if="errorloading">
      <h2> Section Does not Exist! Please Recheck.</h2>
    </div>
    
  </div> 
</template>

<script>
import axios from 'axios';

export default {
  name: 'AddBook',

  props: {
    id: {
      type: String,
      default: null
    }
  },

  data() {
    return {
      newSectionId:'',
      sectionlist:[],
      newBook: {
        name: '',
        author: '',
        cover: null,
        content: null,
        num_pages: '',
        prologue: ''
      },
      errorloading: false,
      isLoading: false,
      idExists: false
    };
  },

  computed: {
    sectionName() {
      return this.sectionlist.find(section => section.id==this.id).name;
    }
  },

  mounted(){
    this.loadSections();
  },

  methods: {
    async loadSections() {
      try {
        const access_token = localStorage.getItem('access_token')
        const response = await axios.get('http://127.0.0.1:5000/api/sections',
            {
                headers:{
                    'Authorization': `Bearer ${access_token}`
                }
            });
            this.sectionlist = response.data;
            if(this.id!=null){
              const section_ids = this.sectionlist.map(section => section.id);
              if (section_ids.includes(parseInt(this.id))) {
                this.idExists = true;
              } else{
                this.errorloading = true;
              }
            } else{
              this.idExists = true;
            }
            
      } catch (error) {
        this.errorloading=true;
        console.error('Error loading sections:', error);
      }
    },

    async addBook() {
        this.isLoading = true;
        try {

        const access_token = localStorage.getItem('access_token');
        const formData = new FormData();
        formData.append('name', this.newBook.name);
        formData.append('author', this.newBook.author);
        formData.append('content', this.newBook.content);
        formData.append('cover', this.newBook.cover);
        formData.append('num_pages', this.newBook.num_pages);
        formData.append('prologue', this.newBook.prologue);

        if(this.id==null){
          formData.append('section_id', this.newSectionId);
        } else{
          formData.append('section_id', this.id);
        }
        await axios.post('http://127.0.0.1:5000/api/books', formData, {
          headers: {
            Authorization: `Bearer ${access_token}`,
            'Content-Type': 'multipart/form-data'
          }
        });

        this.isLoading = false;
        alert('Book added successfully!');
        this.$router.push('/');
      } catch (error) {
        this.isLoading = false;
        alert('Error adding book: ' + error.response.data.message +' Please Retry!');
        console.error('Error adding book:', error);
      }
    },

    handleCoverUpload(event) {
      this.newBook.cover = event.target.files[0];
    },

    handleFileUpload(event) {
      this.newBook.content = event.target.files[0];
    }
  }
};
</script>

<style scoped>
.addbook-view {
    background: url('@/assets/addbooks.jpg') no-repeat center center;
    padding:15px;
    height: 100vh;
    background-size: cover;
}
.add-book-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-title {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.add-book-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

input[type="text"],
input[type="number"],
input[type="file"],
textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
}

textarea {
  resize: vertical;
  height: 100px;
}

.submit-button {
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.submit-button:hover {
  background-color: #45a049;
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
  background-color: rgba(0,0,0,0.4);
}

.modal-content {
  background-color: #fefefe;
  padding: 20px;
  border: 1px solid #888;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
