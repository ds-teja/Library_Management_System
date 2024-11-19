<template>
    <h2>Pay and Download the Book - </h2>
    <div class="payment-container">
      <h2>Card Details</h2>
      <form @submit.prevent="processPayment">
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
        <button type="submit" class="payment-button">Confirm Payment</button>
      </form>
      <div v-if="paymentSuccess" class="payment-success">
        <p>Payment successful! You can now download your book.</p>
        <a :href="bookDownloadUrl" class="download-button">Download Book</a>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        cardNumber: '',
        cardHolder: '',
        expiryDate: '',
        cvv: '',
        paymentSuccess: false,
        bookDownloadUrl: 'path/to/book.pdf' // Change to actual book download URL
      };
    },
    methods: {
      processPayment() {
        // Dummy payment processing logic
        // In a real application, you would integrate with a payment gateway API here
  
        // Simulate a successful payment
        this.paymentSuccess = true;
  
        // Clear the form
        this.cardNumber = '';
        this.cardHolder = '';
        this.expiryDate = '';
        this.cvv = '';
      }
    }
  };
  </script>
  
  <style scoped>
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
  