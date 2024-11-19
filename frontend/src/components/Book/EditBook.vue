<template>
    <div v-if="bookExists">
      <div class="addbook-view"> 
        <div class="add-book-container">
            <h1 class="form-title">Editing Book of {{ newBook.section_name }} Section</h1>
            <form @submit.prevent="editBook" class="add-book-form">
            <div class="form-group">
                <label for="name">Edit Name:</label>
                <input type="text" v-model="newBook.name" id="name" required>
            </div>
            <div class="form-group">
                <label for="author">Edit Author Name:</label>
                <input type="text" v-model="newBook.author" id="author" required>
            </div>
            <div class="form-group">
                <label for="cover">Change Book Cover:</label>
                <input type="file" @change="handleCoverUpload" id="cover">
            </div>
            <div class="form-group">
                <label for="file">Change Book Content:</label>
                <input type="file" @change="handleFileUpload" id="file">
            </div>
            <div class="form-group">
                <label for="num_pages">Edit Number of Pages:</label>
                <input type="number" v-model="newBook.num_pages" id="num_pages" required>
            </div>
            <div class="form-group">
                <label for="prologue">Edit Prologue:</label>
                <textarea v-model="newBook.prologue" id="prologue"></textarea>
            </div>
            <div class="form-group">
                <label for="prologue">Move to another section:</label>
                <select class="form-group" v-model="section_id">
                    <option value="" disabled selected>Move to another Section:</option>
                    <option v-for="section in optionsectionlist" :key="section.id" :value="section.id">{{ section.name }}</option>
                </select>
            </div>
            
            <button type="submit" class="submit-button">Edit Book</button>
            </form>
        </div>
    </div>

    <!-- Modal for loading -->
    <div v-if="isLoading" class="modal">
      <div class="modal-content">
        <p>Changes are uploading, please wait...</p>
      </div>
    </div>
    </div>
    <div v-else>
      <div v-if="errorloading">
        <h2>Book Does not Exist! Please Recheck!</h2>
      </div>
      <div v-if="errorInteger">
        <h2>Book Id Must be an integer, not a string! Please Recheck!</h2>
      </div>
    </div>

  
</template>

<script>
import axios from 'axios';

export default {
  name: 'EditBook',

  props: {
    id: {
      type: String,
      required: true
    }
  },

  data() {
    return {
        sectionslist: [],
        newBook: {
            name: '',
            author: '',
            cover: null,
            content: null,
            num_pages: '',
            prologue: '',
            section_id:''
        },
        section_id:'',
        isLoading: false,
        bookExists: false,
        errorloading: false,
        errorInteger: false
    };
  },

  mounted() {
    this.loadBook();
    this.loadSections();
  },

  computed:{
    optionsectionlist(){
      return this.sectionslist.filter(section => section.id !== this.newBook.section_id);
    }
  },

  methods: {

    async loadBook() {
        try{
          const int_id = parseInt(this.id);
          try {
                const access_token = localStorage.getItem('access_token')
                const response = await axios.get(`http://127.0.0.1:5000/api/books/${int_id}`,
                    {
                        headers:{
                            'Authorization': `Bearer ${access_token}`
                        }
                    });
                this.bookExists = true;
                this.newBook = response.data;
              } 
          catch (error) {
                if(error.response.status==404){
                  this.errorloading=true;
                } 
                console.error('Error loading book:', error);
              }
        } catch(error) {
          this.errorInteger=true;
          return;
        }
    },

    async loadSections() {
      try {
        const access_token = localStorage.getItem('access_token')
        const response = await axios.get('http://127.0.0.1:5000/api/sections',
            {
                headers:{
                    'Authorization': `Bearer ${access_token}`
                }
            });
        this.sectionslist = response.data;
      } catch (error) {
        console.error('Error loading sections:', error);
      }
    },

    async editBook() {
        this.isLoading = true;
        try {
        const access_token = localStorage.getItem('access_token');
        const formData = new FormData();
        formData.append('id', this.id);
        formData.append('name', this.newBook.name);
        formData.append('author', this.newBook.author);
        formData.append('content', this.newBook.content);
        formData.append('cover', this.newBook.cover);
        formData.append('num_pages', this.newBook.num_pages);
        formData.append('prologue', this.newBook.prologue);
        if(this.section_id==''){
            formData.append('section_id',this.newBook.section_id);
        } else{
            formData.append('section_id',this.section_id);
        }
        

        await axios.put('http://127.0.0.1:5000/api/books', formData, {
          headers: {
            Authorization: `Bearer ${access_token}`,
            'Content-Type': 'multipart/form-data'
          }
        });
       
        this.isLoading = false;
        alert('Book Updated successfully!');
        this.$router.push('/');
      } catch (error) {
        this.isLoading = false;
        alert('Error updating book: ' + error.response.data.message);
        console.error('Error updating book:', error);
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
