<template>
    <div v-if="validUser" >
        <div style="display:flex;justify-content:space-between;">
            <h2>{{ bookname }}</h2>
            <div v-if="userRole=='librarian'">
                <button class="download-link" style="margin-top:17px" @click="downloadBook(this.id)">Download Book</button>
            </div>
            <div v-else >
                <button class="download-link" style="margin-top:17px" @click="showPaymentModal()"> Pay and Download Book</button>
            </div>
            
        </div>
        
        <div  class="iframe-container">
        <iframe :src="pdfUrl" width="100%" height="100%" ref="pdfIframe"></iframe>
        </div>
        <!-- Review Submission Form -->
         <div v-if="userRole=='user'">
            <h2>Write your Review</h2>
            <div class="review-form">
                <textarea 
                    v-model="userReview" 
                    :disabled="userReviewSubmitted" 
                    placeholder="Write your review here..."
                    class="review-textarea"
                ></textarea>
                <div class="button-group">
                    <button v-if="userReviewSubmitted" @click="editReview" class="edit-button">Edit</button>
                    <button v-else @click="submitReview" class="submit-button">Submit</button>
                </div>
            </div>
         </div>
         
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

        <div v-if="showPaymentPage" class="modal">
            <div class="modal-content">
                <h2>Pay and Download the Book - {{ bookname }} </h2>
                <div class="payment-container">
                    <h2>Card Details</h2>
                    <form @submit.prevent="downloadBook(this.id)">
                        <div class="form-group">
                        <label for="cardNumber">Card Number:</label>
                        <input type="text" id="cardNumber" v-model="cardNumber" required />
                        </div>
                        <div class="form-group">
                        <label for="cardHolder">Card Holder:</label>
                        <input type="text" id="cardHolder" v-model="cardHolder" required />
                        </div>
                        <div class="form-group">
                        <label for="expiryDate">Expiry Date:</label>
                        <input type="text" id="expiryDate" v-model="expiryDate" required placeholder="MM/YY" />
                        </div>
                        <div class="form-group">
                        <label for="cvv">CVV:</label>
                        <input type="text" id="cvv" v-model="cvv" required />
                        </div>
                        <button type="submit" class="payment-button">Confirm Payment of Rs.{{ book_price }}/-</button>
                    </form>
                    <button @click="cancelPayment()" class="nav-link" style="background-color: sienna;margin-top:10px">Close</button>
                    <div v-if="paymentSuccess" class="payment-success">
                        <p>Payment successful! You can now download your book.</p>
                        <a :href="bookDownloadUrl" class="download-button">Download Book</a>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="isDownloading" class="modal">
            <div class="modal-content">
                <p>Processing Payment, please wait...</p>
            </div>
        </div>
    </div>
    <div v-else>
        <div v-if="errorAuth">
            <h1>You are not authorized to view this book! Please Request for the book.</h1>
            <button @click="goBack">Go Back</button>
        </div>
        <div v-if="errorInteger">
            <h1>Book Id must be an integer. Please Recheck!</h1>
        </div>
        <div v-if="errorId">
            <h1>Book Id Does not exist. Please Recheck!</h1>
        </div>
    </div>
</template>
  
<script>
import axios from 'axios';
import { mapGetters } from 'vuex';

export default {
    name:'ViewBook',

    props: {
        id: {
            type: String,
            required: true
        }
    },

    data() {
        return {
            bookname:'',
            userReview: '',
            pdfUrl: '',
            book_price: '',
            file_name: '',
            validUser: false,
            errorId:false,
            errorInteger:false,
            errorAuth:false,
            userReviewSubmitted: false,
            reviews:[],
            showPaymentPage: false,
            isDownloading:false
        };
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
        this.fetchPDF(this.id);
    },
    
    methods: {
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
                const user_rating = this.reviews.find(review => review.user_id==this.userId);
                if(user_rating){
                    if(user_rating.review!=''){
                            this.userReview=user_rating.review;
                            this.userReviewSubmitted = true;
                    } 
                }
            } catch (error) {
                console.error('Error Fetching Reviews:', error);
            }
        },
        async fetchPDF(bookId) {
                
                try {
                    let int_id = 0;
                    try {
                        int_id = parseInt(bookId);
                    } catch(error){
                        this.errorInteger=true;
                        return;
                    }
                    const access_token = localStorage.getItem('access_token')
                    const response = await axios.get(`http://127.0.0.1:5000/api/books/${int_id}/content`,
                        {
                            headers:{
                                'Authorization': `Bearer ${access_token}`
                            }
                        });
                    if(response.status === 200){
                        this.validUser=true;
                        this.bookname = response.data.name;
                        this.pdfUrl = response.data.book_url;
                        this.book_price = response.data.price;
                        this.file_name = response.data.book_name;
                        this.fetchReviews(int_id);
                    }
                } catch (error) {
                    if(error.response.status==403){
                        this.errorAuth=true;
                    } else if(error.response.status==404){
                        this.errorId=true;
                    }
                    console.error('Error Fetching book:', error);
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
                this.userReviewSubmitted = true;
                this.fetchReviews(this.id);
            } catch (error) {
                console.error('Error Fetching Reviews:', error);
            }
            
        },
        async downloadBook(bookId) {
            try {
                if(this.userRole=='user'){
                    this.showPaymentPage = false;
                    this.isDownloading = true;
                }
                
                const access_token = localStorage.getItem('access_token');
                const response = await axios.get(`http://127.0.0.1:5000/api/books/download/${bookId}`, {
                    responseType: 'blob',
                    headers:{
                        'Authorization':`Bearer ${access_token}`
                    } 
                });
                
                // Create a URL for the file
                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', this.file_name); // or use response.headers to get filename
                document.body.appendChild(link);
                if(this.userRole=='user'){
                    this.isDownloading=false;
                    alert("Payment Succesful! Book is being downloaded...")
                }
                
                link.click();
                
                // Clean up and remove the link
                link.parentNode.removeChild(link);
            } catch (error) {
                console.error('Download failed', error);
            }
        },
        editReview() {
            this.userReviewSubmitted = false;
        },
        goBack() {
            this.$router.go(-1);
        },
        showPaymentModal(){
            this.showPaymentPage=true;
        },
        cancelPayment(){
            this.showPaymentPage = false;
        }
    }
}
</script>

<style scoped>
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

.iframe-container {
  position: relative;
  width: 100%;
  overflow: hidden; 
  height:600px;
}
.review-block{
    background-color: rgb(248, 248, 208);
    border-radius:10px;
    margin:10px;
    padding:5px;
}

.download-link {
    color: white;
    text-decoration: none;
    padding: 8px 16px;
    background-color: #04c033;
    border-radius: 5px;
    border:none;
    transition: background-color 0.3s;
    cursor:pointer;
    margin-right:10px;
}

.download-link:hover {
    background-color: #017c35;
}

.modal {
    z-index:1;
    position:fixed;
    align-items: center;
    justify-content: center;
    left: 0;
    top: 0;
    margin-top:70px;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.4);
}

.modal-content{
    background-color: #fefefe;
    padding: 20px;
    border: 1px solid #888;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.payment-container {
    max-width: 500px;
    margin: 0 auto;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  }
  
  h2 {
    text-align: center;
  }
  
  .form-group {
    margin-bottom: 15px;
  }
  
  label {
    display: block;
    margin-bottom: 5px;
  }
  
  input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 5px;
  }
  
  .payment-button {
    width: 100%;
    padding: 10px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .payment-button:hover {
    background-color: #45a049;
  }
  
  .payment-success {
    text-align: center;
    margin-top: 20px;
  }
  
  .download-button {
    display: inline-block;
    padding: 10px 20px;
    background-color: #008CBA;
    color: white;
    text-decoration: none;
    border-radius: 5px;
    transition: background-color 0.3s;
  }
  
  .download-button:hover {
    background-color: #007bb5;
  }
</style>