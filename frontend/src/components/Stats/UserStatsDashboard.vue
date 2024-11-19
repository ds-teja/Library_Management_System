<template>
  <div v-if="userExists">
    <h1>User Stats</h1>
    <div style="display:flex;gap:10px;justify-content:center;margin:auto">
      <div style="background-color:rgb(240, 238, 238);flex-basis:50%;border-radius: 10px;padding:20px;margin:10px;">
      <h2>Details</h2>
      <h3>Reader since {{ profile.created_date }}</h3>
      <p>Name - {{ profile.name }}</p>
      <p>Email - {{ profile.email }}</p>
      <p>Nationality - {{ profile.nationality }}</p>
      <p>About</p>
      <p>{{profile.about_me}}</p>
      <div v-if="userRole=='user'">
        <button class="edit-button" @click="editProfile()">Edit Profile</button>
        <button class="edit-button" @click="changePassword()">Change Password</button>
      </div>
    </div>

      <div style="background-color:rgb(240, 238, 238);border-radius: 10px;padding:20px;margin:10px;">
      <h2>Requests Summary</h2>
      <p>Total Requests - {{ summary.total_requests }}</p>
      <p>Pending - {{ summary.pending }}</p>
      <p>Withdrawn - {{ summary.withdrawn }}</p>
      <p>Declined - {{ summary.declined }}</p>
      <p>Approved - {{ summary.approved }}</p>
      <p>Returned - {{  summary.returned }}</p>
      <p>Revoked - {{ summary.revoked }}</p>
    </div>

    <div style="background-color:rgb(240, 238, 238);border-radius: 10px;padding:20px;margin:10px">
      <h2>Bookshelves Summary</h2>
      <p>To Read List - {{ summary.to_read }}</p>
      <p>Currently Reading - {{ summary.reading }}</p>
      <p>Completed List - {{ summary.completed }}</p>
    </div>
    </div>
    

    <div  style="background-color:rgb(240, 238, 238); border-radius: 10px;padding:5px;margin:10px 10px 20px 10px">
      <h2>Top 5 Interested Sections</h2>
      <Bar v-if="loaded" :data="SectionsChartData" :options="SectionsChartOptions" :height="120"/>
    </div>

    <div v-if="showEditProfileModal" class="modal">
      <div class="modal-content">
        <span class="close" @click="showEditProfileModal = false">&times;</span>
        <h2>Edit Profile</h2>
        <form @submit.prevent="submitEditProfile" style="display:flex;flex-direction: column;">
          <div>
            <label for="name">Name:</label>
            <input class="input-field" type="text" id="name" v-model="profile.name" required>
          </div>
          <div>
            <label for="email">Email:</label>
            <input  class="input-field" type="email" id="email" v-model="profile.email" required>
          </div>
          <label for="about_me">About Me:</label>
          <textarea id="about_me" v-model="profile.about_me" style="height:150px" required></textarea>
          <button class="edit-button" type="submit" style="margin:10px auto">Save Changes</button>
        </form>
      </div>
    </div>
    <!-- Change Password Modal -->
    <div v-if="showChangePasswordModal" class="modal">
      <div class="modal-content">
        <span class="close" @click="showChangePasswordModal = false">&times;</span>
        <h2>Change Password</h2>
        <form @submit.prevent="submitChangePassword">
          <div style="display:flex;flex-direction: column;">
            <div>
              <label for="new_password">New Password:</label>
              <input class="input-field" type="password" id="new_password" v-model="newPassword" required>
            </div>
            <div>
              <label for="confirm_password">Confirm New Password:</label>
              <input class="input-field" type="password" id="confirm_password" v-model="confirmPassword" required>
            </div>
          </div>
          <button class="edit-button" type="submit" style="margin:10px auto">Change Password</button>
        </form>
      </div>
    </div>
  </div>
  <div v-else>
    <div v-if="errorId">
      <h2>User Does not exist! Please Recheck!</h2>
    </div>
  </div> 
</template>

<script>
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
import axios from 'axios';
import {mapGetters} from 'vuex';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default {
  components: {
    Bar
},
  data(){
    return {
      userExists:false,
      errorId:false,
      newPassword: '',
      confirmPassword: '',
      showEditProfileModal: false,
      showChangePasswordModal: false,
      summary:{},
      profile:{},
      loaded:false,
      SectionsChartData: {
          labels: [],
          datasets: [
              {
                  label: 'Number of Requests',
                  backgroundColor:'#8F3E6E',
                  data: []
              },
              {
                  label: 'Pending',
                  backgroundColor:'#050100',
                  data: [],
              },
              {
                  label: 'Declined',
                  backgroundColor:'#4AB7B0',
                  data: [],
              },
              {
                  label: 'Withdrawn',
                  backgroundColor:'#08309A',
                  data: [],
              },
              {
                  label: 'Approved',
                  backgroundColor:'#5E9B56',
                  data: [],
              },
              {
                  label: 'Returned',
                  backgroundColor:'#E1770E',
                  data: [],
              },
              {
                  label: 'Revoked',
                  backgroundColor:'#E50C4E',
                  data: [],
              }]
      },
      SectionsChartOptions: {
          responsive: true,
      }
    }
  },

  props:{
    id:{
      type:String,
      default:null
    }
  },

  mounted() {
    this.loadProfile()
  },

  computed:{
    ...mapGetters(['userRole'])
  },

  methods:{
    async loadProfile(){
      try { 
        const access_token = localStorage.getItem('access_token')
        if(this.userRole=='user'){
          const response = await axios.get('http://127.0.0.1:5000/user/stats/details',{
            headers:{'Authorization': `Bearer ${access_token}`}
          });
          this.loadSummary(),
          this.fetchPopularSections()
          this.userExists = true;
          this.profile = response.data;
        } else {
          const response = await axios.get(`http://127.0.0.1:5000/user/stats/details?user_id=${this.id}`,{
            headers:{'Authorization': `Bearer ${access_token}`}
          });
          this.loadSummary(),
          this.fetchPopularSections()
          this.userExists = true;
          this.profile = response.data;
        }
      } catch (error) {
        this.errorId=true;
        console.error("Error fetching data:", error);
      }
    },
    async loadSummary(){
      try { 
        const access_token = localStorage.getItem('access_token')
        if(this.userRole=='user'){
          const response = await axios.get('http://127.0.0.1:5000/user/stats/summary',{
            headers:{'Authorization': `Bearer ${access_token}`}
          });
          this.summary = response.data;
        }
        else{
          const response = await axios.get(`http://127.0.0.1:5000/user/stats/summary?user_id=${this.id}`,{
            headers:{'Authorization': `Bearer ${access_token}`}
          });
          this.summary = response.data;
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    },

    async fetchPopularSections() {
      const access_token = localStorage.getItem('access_token')
      if(this.userRole=='user'){
        await axios.get(`http://127.0.0.1:5000/user/stats/sections`,{
          headers:{
                    'Authorization': `Bearer ${access_token}`
                }
        })
        .then((response) => {
          const sections = response.data;
          this.SectionsChartData.labels = sections.map((section) => section.section);
          this.SectionsChartData.datasets[0].data = sections.map((section) => section.request_count);
          this.SectionsChartData.datasets[1].data = sections.map((section) => section.pending);
          this.SectionsChartData.datasets[2].data = sections.map((section) => section.declined);
          this.SectionsChartData.datasets[3].data = sections.map((section) => section.withdrawn);
          this.SectionsChartData.datasets[4].data = sections.map((section) => section.approved);
          this.SectionsChartData.datasets[5].data = sections.map((section) => section.returned);
          this.SectionsChartData.datasets[6].data = sections.map((section) => section.revoked);
          this.loaded = true;
        })
        .catch((error) => {
          console.error('Error fetching popular sections:', error);
        });
      }
      else{
        await axios.get(`http://127.0.0.1:5000/user/stats/sections?user_id=${this.id}`,{
          headers:{
                    'Authorization': `Bearer ${access_token}`
                }
        })
        .then((response) => {
          const sections = response.data;
          this.SectionsChartData.labels = sections.map((section) => section.section);
          this.SectionsChartData.datasets[0].data = sections.map((section) => section.request_count);
          this.SectionsChartData.datasets[1].data = sections.map((section) => section.pending);
          this.SectionsChartData.datasets[2].data = sections.map((section) => section.declined);
          this.SectionsChartData.datasets[3].data = sections.map((section) => section.withdrawn);
          this.SectionsChartData.datasets[4].data = sections.map((section) => section.approved);
          this.SectionsChartData.datasets[5].data = sections.map((section) => section.returned);
          this.SectionsChartData.datasets[6].data = sections.map((section) => section.revoked);
          this.loaded = true;
        })
        .catch((error) => {
          console.error('Error fetching popular sections:', error);
        });
      }
        
    },

    async submitEditProfile() {
        const access_token = localStorage.getItem('access_token');
        const data = {
          'username':this.profile.name,
          'email': this.profile.email,
          'about_me': this.profile.about_me
        }
        await axios.put('http://127.0.0.1:5000/api/auth/users', data, {
          headers: {
            'Authorization': `Bearer ${access_token}`
          }
        });
        this.loadProfile();
        this.showEditProfileModal = false;
    },

    async submitChangePassword() {
      if (this.newPassword !== this.confirmPassword) {
        alert("Password doesn't match!");
        return;
      }
      // API call to change the password
      const access_token = localStorage.getItem('access_token');
        const data = {
          'password':this.newPassword,
        }
        await axios.put('http://127.0.0.1:5000/api/auth/password', data, {
          headers: {
            'Authorization': `Bearer ${access_token}`
          }
        });
        alert("Password updated succesfully!");
        this.showChangePasswordModal = false;
      
    },

    editProfile() {
      this.showEditProfileModal = true;
    },

    changePassword() {
      this.showChangePasswordModal = true;
    }

  }
}
</script>

<style scoped>
.modal {
  position: fixed;
  z-index: 1;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgb(0,0,0);
  background-color: rgba(0,0,0,0.4);
}

.modal-content {
  background-color: #fefefe;
  margin: 15% auto;
  padding: 20px;
  border: 1px solid #888;
  width: 80%;
  border-radius: 10px;
}

.close {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
}

.close:focus {
  color: black;
  text-decoration: none;
  cursor: pointer;
}

.input-field{
  margin:10px;
  width:20%;
  height:30px;
}

.edit-button{
    margin:10px;
    padding:5px;
    width:150px;
    background-color: #9b9999;
    color: white;
    border-radius: 4px;
    cursor: pointer;
}
</style>