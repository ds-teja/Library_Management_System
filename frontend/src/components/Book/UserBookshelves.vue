<template>
    <div class="books-container">
      <button :class="{ 'nav-link': true, 'active': isActive === 'to_read' }" @click="loadAllBooks('To Read List')">To Read List</button>
      <button :class="{ 'nav-link': true, 'active': isActive === 'reading' }" @click="loadAllBooks('Currently Reading')">Currently Reading</button>
      <button :class="{ 'nav-link': true, 'active': isActive === 'completed' }" @click="loadAllBooks('Completed List')">Completed List</button>
      <button :class="{ 'nav-link': true, 'active': isActive === 'favourite' }" @click="loadAllBooks('Favourites')">Favourites</button>
      <button :class="{ 'nav-link': true, 'active': isActive === 'downloaded' }" @click="loadAllBooks('Downloaded')">Downloaded</button>

      <div v-if="isActive==='to_read'">
        <h2>To Read List ({{ this.books_count }})</h2>
      </div>
      <div v-if="isActive==='reading'">
        <h2>Currently Reading List ({{ this.books_count }})</h2>
      </div>
      <div v-if="isActive==='completed'">
        <h2>Completed List ({{ this.books_count }})</h2>
      </div>
      <div v-if="isActive==='favourite'">
        <h2>Favourites List ({{ this.books_count }})</h2>
      </div>
      <div v-if="isActive==='downloaded'">
        <h2>Downloaded Books ({{ this.books_count }})</h2>
      </div>

      <input type="text" v-model="searchQuery" placeholder="Search books..." class="search-input" />
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
          <p><strong>Genre:</strong> {{ book.section_name }}</p>
          <button style="width:97%;color:white;background-color:#50565e;border:none;cursor:pointer;height:25px;border-radius:3px">Know More</button>
          <div class="button-container">
            <button v-if="book.req_status=='NoRequest' && book.isDownloaded==false" class="request-button" @click="addRequest(book)">
              <strong>Request</strong>
            </button>
            <router-link v-if="book.req_status=='Pending'" class="request-button" style="text-decoration: none;background-color: #035dd3;" to='/mybooks'>
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
            <button v-if="book.showSaveButton" class="save-button" @click="reloadPage()">
              Cancel
            </button>
          </div>
        </div>
      </div>
      <div v-else>
        <p>No Books available in this section.</p>
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
        isActive: 'to_read',
        bookslist: [],
        heartOutline,
        heartFilled,
        searchQuery: '',
        books_count:0
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
        this.loadAllBooks("To Read List");
    },
  
    methods: {
      async loadAllBooks(shelf) {
        if(shelf=='Favourites'){
          this.isActive = 'favourite';
          try {
            const access_token = localStorage.getItem('access_token')
            const response = await axios.get(`http://127.0.0.1:5000/api/books/user?fav=true`,
                {
                    headers:{
                        'Authorization': `Bearer ${access_token}`
                    }
                });
            this.bookslist = response.data.books_info;
            this.books_count = response.data.books_count;
          } catch (error) {
            console.error('Error loading books:', error);
          }
        } else if(shelf=='Downloaded'){
          this.isActive = 'downloaded';
          try {
            const access_token = localStorage.getItem('access_token')
            const response = await axios.get(`http://127.0.0.1:5000/api/books/user?downloaded=true`,
                {
                    headers:{
                        'Authorization': `Bearer ${access_token}`
                    }
                });
            this.bookslist = response.data.books_info;
            this.books_count = response.data.books_count;
          } catch (error) {
            console.error('Error loading books:', error);
          }
        }
         else{
          if(shelf=='To Read List'){
            this.isActive='to_read';
          } else if (shelf=='Currently Reading'){
            this.isActive='reading';
          } else if (shelf=='Completed List'){
            this.isActive='completed'
          } else{
            return;
          }
          try {
            const access_token = localStorage.getItem('access_token')
            const response = await axios.get(`http://127.0.0.1:5000/api/books/user?shelf=${shelf}`,
                {
                    headers:{
                        'Authorization': `Bearer ${access_token}`
                    }
                });
            this.bookslist = response.data.books_info;
            this.books_count = response.data.books_count;
          } catch (error) {
            console.error('Error loading books:', error);
          }
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
              {
                  headers:{
                      'Authorization': `Bearer ${access_token}`
                  }
              });
          this.reloadPage();
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
          this.reloadPage();
        } catch (error) {
          console.error('Error adding preferences:', error);
        }
        book.showSaveButton = false; 
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
              this.reloadPage();
            } catch (error) {
              book.isFavourite = !book.isFavourite;
              console.error('Error adding preferences:', error);
            }
        }
      },

      reloadPage(){
        if (this.isActive=='favourite') {
          this.loadAllBooks("Favourites");
        } else if(this.isActive=='to_read'){
          this.loadAllBooks("To Read List");
        } else if(this.isActive=='reading'){
          this.loadAllBooks("Currently Reading");
        } else if(this.isActive=='completed'){
          this.loadAllBooks("Completed List");
        } else if(this.isActive=='downloaded'){
          this.loadAllBooks("Downloaded");
        }
      }
    }
  }
  </script>
  
  
  <style scoped>
  .books-container {
    padding: 20px;
  }
  
  h2 {
    text-align: center;
    margin-bottom: 20px;
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
    z-index: 1;
  }
  
  .favourite-icon img {
    width: 24px;
    height: 24px;
  }
  
  .save-button {
    margin: 5px;
  }

  .nav-link.active {
  background-color: #033b61;
  color: white;
}
  </style>