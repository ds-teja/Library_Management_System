<template>
    <div v-if="bookExists">
    <div  class="book-details-container">
      <img :src="ProvideUrl(newBook.cover_url)" alt="Cover image" class="book-cover">
      <div class="book-info">
        <h2 class="book-title">{{ newBook.name }}</h2>
        <h4 class="book-author">by {{ newBook.author }}</h4>
        <p class="book-section">Genre: {{ newBook.section_name }}</p>
        <p class="book-pages">Number of Pages: {{ newBook.num_pages }}</p>
        <h3> Prologue: </h3>
        <p class="book-prologue">{{ newBook.prologue }}</p>
      </div>
    </div>
    <!-- Review Submission Form -->
    <div v-if="userRole=='user'">
            <h2>Write your Review</h2>
            <div class="review-form">
                <textarea 
                    v-model="this.userReview" 
                    :disabled="userReviewSubmitted" 
                    placeholder="Write your review here..."
                    class="review-textarea"
                ></textarea>
                <div class="button-group">
                    <button v-if="userReviewSubmitted" @click="editReview('edit')" class="edit-button">Edit</button>
                    <button v-if="userReviewSubmitted" @click="editReview('delete')" class="edit-button">Delete</button>
                    <button v-else @click="submitReview" class="edit-button">Submit</button>
                </div>
            </div>
         </div>
    <div>
        <h2>{{reviewsCount}} Reviews</h2>
        <div v-for="review in reviews" :key="review.id">
            <div class="review-block">
                <div style="display:flex;gap:10px;margin:5px">
                    <h4>{{review.username}}</h4>
                    <p>{{computeRating(review.rating)}}</p>
                </div>
                <p>{{ review.review }}</p>
            </div>
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
import {mapGetters} from 'vuex';
import noCover from '@/assets/no-cover-available.png';

export default {
    name:'KnowMore',

    props: {
        id:{
            type:String,
            required:true
        }
    },

    data() {
        return{
            bookExists: false,
            errorloading: false,
            errorInteger: false,
            newBook: {},
            reviews: [],
            userReview: '',
            userReviewSubmitted: false
        }
    },

    computed: {
        ...mapGetters(['userId','userRole']),
        reviewsCount(){
            return this.reviews.length;
        },
        computeRating() {
            return function(rating) {
                if (rating != null) {
                    const stars = '⭐'.repeat(rating[0]);
                    return stars;
                } else {
                    return rating;
                }
            }
        },

    },

    mounted() {
        this.loadBook()
    },

    methods: {
        async loadBook(){
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
                        this.fetchReviews(int_id);
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

        async fetchReviews(bookId){
            try {
                const access_token = localStorage.getItem('access_token')
                const response = await axios.get(`http://127.0.0.1:5000/api/reviews?book_id=${bookId}`,
                    {
                        headers:{
                            'Authorization': `Bearer ${access_token}`
                        }
                    });
                this.reviews = response.data;
                console.log("ok....")
                if(this.userRole=='user'){
                    const user_rating = this.reviews.find(review => review.user_id==this.userId);
                    if(user_rating){
                        if(user_rating.review!=''){
                            this.userReview=user_rating.review;
                            this.userReviewSubmitted = true;
                        } 
                    }
                }
            } catch (error) {
                console.error('Error Fetching Reviews:', error);
            }
        },

        ProvideUrl(cover_url){
            if(cover_url == ''){
                return noCover;
            } else{
                return cover_url;
            }
        },

        async submitReview() {
            try {
                const data ={
                    'book_id':this.id,
                    'review':this.userReview
                }
                const access_token = localStorage.getItem('access_token');
                await axios.post(`http://127.0.0.1:5000/api/reviews`,data,
                    {
                        headers:{
                            'Authorization': `Bearer ${access_token}`
                        }
                    }
                );
                if(this.userReview==''){
                    alert("Review Deleted Succesfully!");
                } else{
                    alert("Review Posted Succesfully!");
                    this.userReviewSubmitted = true;
                }
                this.fetchReviews(this.id);
            } catch (error) {
                console.error('Error Fetching Reviews:', error);
            }
            
        },
        editReview(option) {
            if(option=='delete'){
                this.userReview='';
                this.submitReview();
                this.userReviewSubmitted = false;
            } else if(option=='edit'){
                this.userReviewSubmitted = false;
            }
        },
    }
}
</script>

<style scoped>
.book-details-container {
  margin:20px;
  display: flex;
  gap: 20px;
  justify-content: center;
  padding: 20px;
  background-color: #e2e2e2;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.book-cover {
  width: 300px;
  height: 400px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.book-info {
  display: flex;
  flex-direction: column;
}

.book-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
  color: #333;
}

.book-author {
  font-size: 1.2rem;
  font-weight: normal;
  color: #555;
}

.review-form {
    margin-bottom: 20px;
}

.review-textarea {
    width: 80%;
    height: 100px;
    padding: 10px;
    margin: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
    font-size: 14px;
    resize: vertical;
}

.review-textarea:disabled {
    background-color: #f5f5f5;
}

.review-block{
    background-color: rgb(248, 248, 208);
    border-radius:10px;
    margin:10px;
    padding:5px;
}

.edit-button{
    margin:10px;
    padding:5px;
    width:100px;
    background-color: #9b9999;
    color: white;
    border-radius: 4px;
    cursor: pointer;
}
</style>
