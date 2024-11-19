<template>
  <div>
    <h1>My Book Requests</h1>
    <button 
      @click="showActive" 
      :class="{ 'nav-link': true, 'active': isActive === 'active' }">
      Active Requests
    </button>
    <button 
      @click="showHistory" 
      :class="{ 'nav-link': true, 'active': isActive === 'history' }">
      History of Requests
    </button>
  </div>
  <div v-if="isActive === 'active'">
    <h2>Active Book Requests ({{ this.active_count }})</h2>
    <table class="requests-table">
      <thead>
        <tr>
          <th>Book Name</th>
          <th>Requested Date</th>
          <th>Request Status</th>
          <th>Actions</th>
          <th>Issued Date</th>
          <th>Expiry Date</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="request in this.active_requests" :key="request.req_id">
          <td>{{ request.name }}</td>
          <td>{{ String(request.req_date).split('GMT')[0] }}</td>
          <td>{{ request.req_status }}</td>
          <td>
            <button v-if="request.req_status == 'Pending'" @click="updateRequest(request.req_id, 'withdraw')">Withdraw Request</button>
            <button v-if="request.req_status == 'Approved'" @click="viewBook(request.book_id)">Enjoy Reading - View Book</button>
            <button v-if="request.req_status == 'Approved'" @click="updateRequest(request.req_id, 'return')">Return Book</button>
          </td>
          <td>{{ request.issued_date }}</td>
          <td>{{ request.expiry_date }}</td>
        </tr>
      </tbody>
    </table>
    <div v-if="isloading" class="modal">
      <div class="modal-content">
        <p>Book is being returned, please wait...</p>
      </div>
    </div>
  </div>
  <div v-else>
    <h2>History of Book Requests ({{ this.inactive_count }})</h2>
    <table class="requests-table">
      <thead>
        <tr>
          <th>Book Name</th>
          <th>Requested Date</th>
          <th>Actions</th>
          <th>Issued Date</th>
          <th>Return Date</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="request in this.inactive_requests" :key="request.req_id">
          <td>{{ request.name }}</td>
          <td>{{ String(request.req_date).split('GMT')[0] }}</td>
          <td>{{ request.req_status }}</td>
          <td>{{ request.issued_date }}</td>
          <td>{{ request.return_date }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>


<script>
import axios from 'axios';
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'ActiveBookList',

  data() {
    return {
      active_requests: [],
      inactive_requests: [],
      active_count:0,
      inactive_count:0,
      isActive: 'active',
      isloading:false,
    };
  },

  computed: {
    ...mapGetters(['userId']),
  },

  mounted() {
    this.loadRequestData();
  },

  methods: {
    ...mapActions(['logout']),
    async loadRequestData() {
      try {
        const access_token = localStorage.getItem('access_token');
        const response = await axios.get(`http://127.0.0.1:5000/api/requests/${this.userId}`, {
          headers: {
            'Authorization': `Bearer ${access_token}`
          }
        });
        this.active_requests = response.data.active_requests;
        this.active_count = response.data.active_count;

        this.inactive_requests = response.data.inactive_requests;
        this.inactive_count = response.data.inactive_count;
      } catch (error) {
        console.error('Error loading books:', error);
      }
    },
    async updateRequest(requestId, new_status) {
      const userConfirmed = confirm(`Are you sure you want to ${new_status}?`);
      if (userConfirmed) {
        try {
          const access_token = localStorage.getItem('access_token');
          if (new_status == 'return') {
            this.isloading=true;
            await axios.put(`http://127.0.0.1:5000/api/requests/user`, { 'request_id': requestId, 'req_status': 'Returned' }, {
              headers: {
                Authorization: `Bearer ${access_token}`
              }
            });
            this.isloading=false;
            alert("Book Returned successfully!");
          } else if (new_status == 'withdraw') {
            await axios.put(`http://127.0.0.1:5000/api/requests/user`, { 'request_id': requestId, 'req_status': 'Withdrawn' }, {
              headers: {
                Authorization: `Bearer ${access_token}`
              }
            });
            alert('Request withdrawn!');
          }
          this.loadRequestData();
        } catch (error) {
          console.error('Error updating request:', error);
        }
      } else {
        alert('Canceled!');
      }
    },
    async viewBook(book_id) {
      this.$router.push(`/viewbook/${book_id}`);
    },
    showHistory() {
      this.isActive = 'history';
    },
    showActive() {
      this.isActive = 'active';
    },
    calculateExpirynDate(issuedDate) {
      if (!issuedDate) return '';
      const date = new Date(issuedDate);
      date.setDate(date.getDate() + 6);
      return String(date).split('GMT')[0];
    }
  }
};
</script>


<style scoped>
.requests-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.requests-table th, .requests-table td {
  border: 1px solid #ddd;
  padding: 8px;
}

.requests-table th {
  background-color: #f2f2f2;
  text-align: left;
}

.requests-table tr:nth-child(even) {
  background-color: #f9f9f9;
}

.requests-table tr:hover {
  background-color: #ddd;
}

.requests-table th, .requests-table td {
  padding: 12px;
  text-align: left;
}

.requests-table button {
  margin-right: 5px;
  padding: 5px 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.requests-table button:hover {
  background-color: #45a049;
}

.requests-table button:last-child {
  background-color: #f44336;
}

.requests-table button:last-child:hover {
  background-color: #e53935;
}

.nav-link.active {
  background-color: #033b61;
  color: white;
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
