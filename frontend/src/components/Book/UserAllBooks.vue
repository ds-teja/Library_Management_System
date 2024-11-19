<template>
  <div v-if="sectionExist" class="books-container">
    <div v-if="this.id!=null">
        <h2>{{this.section_name}} Books ({{ this.books_count }})</h2>
      </div>
      <div v-else>
        <h2>All Books ({{ this.books_count }})</h2>
      </div>


    <input type="text" v-model="searchQuery" placeholder="Search books, authors, genres..." class="search-input" />
    <div v-if="filteredBooks.length > 0" class="books-grid">
      <div v-for="book in filteredBooks" :key="book.id" class="book-card">
        <div style="display:flex;gap:27%">
          <div class="favourite-icon" @click="toggleFavourite(book)">
            <img :src="book.isFavourite ? heartFilled : heartOutline" alt="Favourite">
          </div>
          <img :src="ProvideUrl(book.cover_url)" alt="Cover image" class="book-cover">
        </div>
        
        <h3>{{ book.name }}</h3>
        <p><strong>Author:</strong> {{ book.author }}</p>
        <button style="background-color: none; text-decoration: underline;border:none;cursor:pointer;margin:5px;" @click="toSection(book.section_id)"><strong>Genre:</strong> {{ book.section_name }}</button>
        <button @click="knowMore(book.id)" style="width:97%;color:white;background-color:#50565e;border:none;cursor:pointer;height:25px;border-radius:3px">Know More</button>
        <div class="button-container">
          <button v-if="book.req_status=='NoRequest' && book.isDownloaded==false" class="request-button" @click="addRequest(book)">
            <strong>Request</strong>
          </button>
          <router-link v-if="book.req_status=='Pending'" class="request-button" style="text-decoration: none;background-color: #035dd3;" to='/user-dashboard/requests'>
            <strong>Check Request Status</strong>
          </router-link>
          <button v-if="book.req_status=='Approved'" class="request-button" @click="viewBook(book.id)" style="color:black;background-color: lightgreen;">
            <strong>Approved - View Book</strong>
          </button>
          <button v-if="book.isDownloaded" class="request-button" @click="viewBook(book.id)" style="color:black;background-color: lightgreen;">
            <strong>Downloaded - View Book</strong>
          </button>
          <select  v-model="book.selectedShelf" @change="checkChanges(book)"  class="bookshelf-select">
            <option value="" disabled selected>Add to Bookshelves</option>
            <option>To Read List</option>
            <option>Currently Reading</option>
            <option>Completed List</option>
          </select>
          <select  v-model="book.selectedRating" @change="checkChanges(book)" class="rating-select">
            <option value="" disabled selected>Rating</option>
            <option>1⭐</option>
            <option>2⭐</option>
            <option>3⭐</option>
            <option>4⭐</option>
            <option>5⭐</option>
          </select>
        </div>
        <div>
          <button v-if="book.showSaveButton" class="save-button" @click="saveChanges(book)">
            Save Changes
          </button>
          <button v-if="book.showSaveButton" class="save-button" @click="cancelChanges">
            Cancel
          </button>
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
import {mapGetters} from 'vuex';
import heartOutline from '@/assets/heart-outline.png';
import heartFilled from '@/assets/heart-filled.png';
import noCover from '@/assets/no-cover-available.png';

export default {
  name:'BookList',

  data() {
    return {
      bookslist: [],
      heartOutline,
      heartFilled,
      searchQuery: '',
      sectionExist: false,
      loaded:false,
      section_name:'',
      books_count:0
    }
  },

  props:{
    id:{
      type: String,
      default: null
    }
  },

  computed: {
    ...mapGetters(['userId']),

    filteredBooks() {
      return this.bookslist.filter(book => {
        return book.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
               book.author.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
               book.section_name.toLowerCase().includes(this.searchQuery.toLowerCase());
      });
    }
  },

  mounted() {
    if (this.id === null) {
      this.loadAllBooks();
    } else {
      this.loadSectionBooks();
    }
  },

  methods: {
    async loadAllBooks() {
      try {
        const access_token = localStorage.getItem('access_token')
        const response = await axios.get(`http://127.0.0.1:5000/api/books/user`,
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
        const response = await axios.get(`http://127.0.0.1:5000/api/books/user?section_id=${this.id}`,
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

    async addRequest(book) {
      const request_info = {
        req_user_id: this.userId,
        req_book_id: book.id,
        req_date: new Date().toISOString(),
        req_status: 'Pending'
      };
      try {
        const access_token = localStorage.getItem('access_token')
        await axios.post(`http://127.0.0.1:5000/api/requests`, request_info,
            {headers:{'Authorization': `Bearer ${access_token}`}});
        alert("Request sent to the admin.");
        if (this.id === null) {
          this.loadAllBooks();
        } else {
          this.loadSectionBooks();
        }
      } catch (error) {
        if (error.response && error.response.status === 400) {
          alert("You have Reached Maximum Active Books Limit!");
        } else {
          console.error('Error loading books:', error);
        }
      }
    },

    ProvideUrl(cover_url){
      if(cover_url == ''){
        return noCover;
      } else{
        return cover_url;
      }
    },

    async viewBook(book_id){
        this.$router.push(`/viewbook/${book_id}`)
    },

    checkChanges(book) {
      // checking if any of these two are not empty
      book.showSaveButton = !!book.selectedShelf || !!book.selectedRating; 
    },

    async saveChanges(book) {
      try {
        const access_token = localStorage.getItem('access_token')
        await axios.post(`http://127.0.0.1:5000/api/rating`, book,
            {
                headers:{
                    'Authorization': `Bearer ${access_token}`
                }
            });
            if (this.id === null) {
              this.loadAllBooks();
            } else {
              this.loadSectionBooks();
            }
      } catch (error) {
        console.error('Error adding preferences:', error);
      }
      book.showSaveButton = false; 
    },

    async cancelChanges(){
      if (this.id === null) {
        this.loadAllBooks();
      } else {
        this.loadSectionBooks();
      }
    },

    async knowMore(bookId){
      this.$router.push(`/book/details/${bookId}`);
    },

    async toggleFavourite(book) {
      var performAction = false;
      if(book.isFavourite){
        const res = confirm("Are you sure, you want to remove this book from favourites?");
        if(res){
          performAction = true;
        }
      } else {
        const res = confirm("Are you sure, you want to add this book to favourites?");
        if(res){
          performAction = true;
        }
      }

      if(performAction){
        book.isFavourite = !book.isFavourite;
          try {
            const access_token = localStorage.getItem('access_token')
            await axios.post(`http://127.0.0.1:5000/api/favourite`, book,
                {
                    headers:{
                        'Authorization': `Bearer ${access_token}`
                    }
                });
                if (this.id === null) {this.loadAllBooks();} 
                else {this.loadSectionBooks();}
          } catch (error) {
            book.isFavourite = !book.isFavourite;
            console.error('Error adding preferences:', error);
          }
      }
    },

    async toSection(section_id){
      this.$router.push(`/user-dashboard/section/${section_id}`)
    }
  }
}
</script>


<style scoped>
.books-container {
  padding: 20px;
}
.search-input {
  display: block;
  margin: 0 auto 20px auto;
  padding: 10px;
  width: 80%;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 4px #60656d;
}
.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
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
  background-color: #fff8f8;
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
}

.request-button {
  width:100%;
  padding: 10px;
  margin: 5px;
  border: none;
  border-radius: 4px;
  background-color: #50565e;
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.request-button:hover {
  background-color: #0056b3;
}

.select-container {
  margin-top: 10px;
}

select {
  padding: 8px;
  margin: 5px;
  border: 1px solid #ddd;
  color: white;
  border-radius: 4px;
  background-color: #50565e;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s;
}

select:focus {
  outline: none;
  border: none;
}

.favourite-icon {
  flex-basis:1%;
  top: 10px;
  left: 10px;
  cursor: pointer;
}

.favourite-icon img {
  width: 24px;
  height: 24px;
}

.save-button {
  margin: 5px;
}
</style>