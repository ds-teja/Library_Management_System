<template>
    <div v-if="sectionExist" class="books-container">
      <div v-if="this.id!=null" class="nav-books">
        <h2 style="margin-left: 40vw;">{{this.section_name}} Books ({{ this.books_count }})</h2>
        <button @click="addbookToSection(this.id)" class="add-button" style="margin-right:0">Add New Book to {{this.section_name}} section</button>
      </div>
      <div v-else  class="nav-books">
        <h2 style="margin-left: 40vw;">All Books ({{ this.books_count }})</h2>
        <button @click="addbook" class="add-button" style="margin-right:0">Add New Book to any existing section</button>
      </div>
      
      <div v-if="filteredBooks.length > 0">
        <input type="text" v-model="searchQuery" placeholder="Search books..." class="search-input" />
        <div class="books-grid">
          <div v-for="book in filteredBooks" :key="book.id" class="book-card">
            <img :src="ProvideUrl(book.cover_url)" alt="Cover image" class="book-cover">
            
            <h3>{{ book.name }}</h3>
            <p><strong>Author:</strong> {{ book.author }}</p>
            <button style="background-color: none; text-decoration: underline;border:none;cursor:pointer;margin:5px;" @click="toSection(book.section_id)"><strong>Genre:</strong> {{ book.section_name }}</button>
            <button @click="knowMore(book.id)" style="width:97%;color:white;background-color:#50565e;border:none;cursor:pointer;height:25px;border-radius:3px">Know More</button>
            <div class="button-container">
              <button class="changes-button" @click="viewRequests(book)"><strong>View Requests</strong></button>
              <button class="changes-button" @click="viewBook(book)"><strong>View Book</strong></button>
              <button class="changes-button" @click="editBook(book.id)"><strong>Edit Book</strong></button>
              <button class="changes-button"  @click="deleteBook(book.id)"><strong>Delete Book</strong></button>
            </div>
          </div>
        </div>
        
      </div>
      <div v-else>
        <div v-if="this.id!=null">
          <p>No Books available in this section.</p>
        </div>
        <div v-else>
          <p>No Books available.</p>
        </div>
        
      </div>
    </div>
    <div v-else>
      <div v-if="loaded">
        <h2>Section Does Not Exist! Please Recheck.</h2>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import noCover from '@/assets/no-cover-available.png';
  
  export default {
  name:'LibrarianAllBooks',
  
  data() {
      return {
          bookslist:[],
          searchQuery: '',
          sectionExist: false,
          section_name:'',
          loaded:false,
          books_count:0
      }
  },

  computed: {
    filteredBooks() {
      return this.bookslist.filter(book => {
        return book.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
               book.author.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
               book.section_name.toLowerCase().includes(this.searchQuery.toLowerCase());
      });
    }
  },

  props:{
    id:{
      type: String,
      default: null
    }
  },
  
  mounted() {
    if (this.id === null) {
      this.loadAllBooks();
    } else {
      this.loadSectionBooks();
    }
  },
  
  watch: {
    $route(to, from) {
      if (to.path !== from.path) {
        if (this.id === null) {
          this.loadAllBooks();
        } else {
          this.loadSectionBooks();
        }
      }
    }
  },
  
  methods: {
      async loadAllBooks() {
        try {
          const access_token = localStorage.getItem('access_token')
          const response = await axios.get(`http://127.0.0.1:5000/api/books/librarian`,
              {
                  headers:{
                      'Authorization': `Bearer ${access_token}`
                  }
              });
          this.sectionExist = true;
          this.bookslist = response.data.books_info;
          this.books_count = response.data.books_count;
        } catch (error) {
          console.error('Error loading books:', error);
        }
      },

      async loadSectionBooks() {
        try {
          const access_token = localStorage.getItem('access_token')
          const response = await axios.get(`http://127.0.0.1:5000/api/books/librarian?section_id=${this.id}`,
              {
                  headers:{
                      'Authorization': `Bearer ${access_token}`
                  }
              });
          this.sectionExist = true;
          this.section_name = response.data.section_name;
          this.bookslist = response.data.books_info;
          this.books_count = response.data.books_count;
        } catch (error) {
          if(error.response.status==404){
            this.loaded=true;
          }
          console.error('Error loading books:', error);
        }
      },
  
      ProvideUrl(cover_url){
        if(cover_url==''){
          return noCover;
        }else{
          return cover_url;
        }
      },
      
    async viewRequests(book){
      this.$router.push(`/librarian-dashboard/books/requests/${book.id}`);
    },

    async knowMore(bookId){
      this.$router.push(`/book/details/${bookId}`);
    },

    async addbook() {
      this.$router.push(`/librarian-dashboard/addbook`)
    },

    async addbookToSection(bookId) {
      this.$router.push(`/librarian-dashboard/addbook/${bookId}`)
    },

    async viewBook(book){
      this.$router.push(`/viewbook/${book.id}`)
    },

    async editBook(book_id){
      this.$router.push(`/librarian-dashboard/editbook/${book_id}`)
    },

    async deleteBook(bookId){
      if(confirm("Are you sure you want to delete the book?")){
        try {
        const access_token = localStorage.getItem('access_token')
        await axios.delete(`http://127.0.0.1:5000/api/books/${bookId}`,
            {
                headers:{
                    'Authorization': `Bearer ${access_token}`
                }
            });
            alert("Book Delete Succesfully!");
            if (this.id === null) {
              this.loadAllBooks();
            } else {
              this.loadSectionBooks();
            }
      } catch (error) {
        alert("Error Deleting Book. Please Retry!");
        console.error('Error Deleting book:', error);
      }
      }
    },

    async toSection(section_id){
      this.$router.push(`/librarian-dashboard/allbooks/${section_id}`)
    }
  
  }
  
  }
  </script>
  
  <style scoped>
.nav-books{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin:auto;
  width:95%;
}
.search-input {
  display: block;
  margin: 0 auto 20px auto;
  padding: 10px;
  width: 94%;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 4px #60656d;
}

.add-button {
  display: block;
  margin: 20px auto;
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.add-button:hover {
  background-color: #45a049;
}
  .books-container {
    padding: 20px;
  }
  
  h2 {
    text-align: center;
    margin-bottom: 20px;
  }
  
  .books-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 20px;
    width:95%;
    margin:auto
  }
  
  .book-card {
    background-color: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .book-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
  }
  
  .book-cover {
    max-width: 500px;
    height: 250px;
    border-radius: 4px;
    align-content: center;
  }
  
  .button-container {
    display: flex;
    align-content: center;
    gap:2px;
    padding:5px;
  }
  .changes-button {
    margin:5px 4px;
    padding:8px;
    border-radius: 5px;
    border: none;
    background-color: #7d8086;
    color:white;
    cursor:pointer;
  }
  .changes-button:hover{
    background-color:rgb(36, 76, 187);
  }
  </style>