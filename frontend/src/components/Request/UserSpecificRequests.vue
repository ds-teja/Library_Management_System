<template>
  <div v-if="userExist">
    <div v-if="requestsExist">
      <h1 v-if="loaded">Requests of User {{ this.user_name }}</h1>
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
    
      <div v-if="isActive === 'active'">
        <h2>Active Book Requests ({{ this.active_count }})</h2>
        <table class="requests-table">
          <thead>
            <tr>
              <th>User ID</th>
              <th>User Name</th>
              <th>Book Name</th>
              <th>Requested Date</th>
              <th>Request Status</th>
              <th>Actions</th>
              <th>Issued Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in this.active_requests" :key="request.id">
              <td>{{ request.user_id }}</td>
              <td>{{ request.user_name }}</td>
              <td>{{ request.book_name }}</td>
              <td>{{ String(request.req_date).split('GMT')[0] }}</td>
              <td>{{ request.req_status }}</td>
              <td>
                <button v-if="request.req_status=='Pending'" @click="updateRequest(request.id,'approve')">Approve</button>
                <button v-if="request.req_status=='Pending'" @click="updateRequest(request.id,'decline')">Decline</button>
                <button v-if="request.req_status=='Approved'" @click="updateRequest(request.id, 'revoke')">Revoke Access</button>
              </td>
              <td>{{ request.issued_date }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else>
        <h2>History of Book Requests ({{ this.inactive_count }})</h2>
        <table class="requests-table">
          <thead>
            <tr>
              <th>User ID</th>
              <th>User Name</th>
              <th>Book Name</th>
              <th>Requested Date</th>
              <th>Actions</th>
              <th>Issued Date</th>
              <th>Return Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in this.inactive_requests" :key="request.id">
              <td>{{ request.user_id }}</td>
              <td>{{ request.user_name }}</td>
              <td>{{ request.book_name }}</td>
              <td>{{ String(request.req_date).split('GMT')[0] }}</td>
              <td>{{ request.req_status }}</td>
              <td>{{ request.issued_date }}</td>
              <td>{{ request.return_date }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else>
      <div v-if="loaded">
        <h2>No Available Requests of the User!</h2>
      </div>
    </div>
  </div>
  <div v-else>
    <div v-if="loaded">
      <h2>User Does not exist! Please Re-check!</h2>
    </div>
  </div>
</template>
    
    <script>
    import axios from 'axios';
    
    export default {
      name: 'AllRequests',
  
      data() {
        return {
          loaded:false,
          active_requests: [],
          active_count:0,
          inactive_requests:[],
          inactive_count:0,
          isActive: 'active',
          requestsExist: false,
          user_name:'',
          userExist: false
        };
      },

      props:{
        id:{
            type:String,
            required:true
        }
      },
  
      mounted() {
        this.loadRequests();
      },
  
      methods: {
        async loadRequests() {
          try {
            const access_token = localStorage.getItem('access_token');
            const response = await axios.get(`http://127.0.0.1:5000/api/requests?user_id=${this.id}`, {
              headers: {
                Authorization: `Bearer ${access_token}`
              }
            });
            this.userExist=true;
           
            this.active_requests = response.data.active_requests;
            this.active_count = response.data.active_count;
            this.inactive_requests = response.data.inactive_requests;
            this.inactive_count = response.data.inactive_count;
            
            if(this.active_count!=0 || this.inactive_count!=0){
              this.requestsExist=true;
              if(this.active_count!=0){
                this.user_name=this.active_requests[0]['user_name'];
              } else{
                this.user_name=this.inactive_requests[0]['user_name'];
              }
            }
            this.loaded=true;
          } catch (error) {
            this.loaded=true;
            console.error('Error loading requests:', error);
          }
        },
        async updateRequest(requestId, new_status) {
          try {
            const access_token = localStorage.getItem('access_token');
            if(new_status == 'approve'){
              await axios.put(`http://127.0.0.1:5000/api/requests`, {'request_id':requestId,'req_status':'Approved'}, {
                headers: {
                  Authorization: `Bearer ${access_token}`
                }
              });
            } 
            else if (new_status == 'decline') {
              await axios.put(`http://127.0.0.1:5000/api/requests`, {'request_id':requestId,'req_status':'Declined'}, {
              headers: {
                Authorization: `Bearer ${access_token}`
               }
              });
            }
            else if (new_status == 'revoke') {
              await axios.put(`http://127.0.0.1:5000/api/requests`, {'request_id':requestId,'req_status':'Revoked'}, {
              headers: {
                Authorization: `Bearer ${access_token}`
               }
              });
            }
            this.loadRequests();
          } catch (error) {
            console.error('Error updating request:', error);
          }
        },
        showHistory() {
      this.isActive = 'history';
    },
    showActive() {
      this.isActive = 'active';
    },
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
    </style>
    