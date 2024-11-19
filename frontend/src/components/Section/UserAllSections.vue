<template>
  <div>
    <div class="dashboard">
      <h2>All Sections</h2>
      <input type="text" v-model="searchQuery" placeholder="Search sections..." class="search-input" />
      <div v-if="filteredSections.length > 0" class="section-container">
        <div v-for="section in filteredSections" :key="section.id" class="section-card">
          <img :src="ProvideUrl(section.cover_url)" alt="Section Cover" class="section-cover">
          <h3 class="section-title">{{ section.name }}</h3>
          <p><strong>Created Date:</strong> {{ formatDate(section.created_date) }}</p>
          <p><strong>Description:</strong> {{ section.description }}</p>
          <button @click="viewbooks(section)" class="action-button">View Books</button>
        </div>
      </div>
      <div v-else>
        <p class="no-sections-message">No sections available.</p>
      </div>
    </div>
  </div>
</template>


<script>
import axios from 'axios';
import { mapActions } from 'vuex';
import noCover from '@/assets/no-image-available.jpg';

export default {
  name: 'SectionList',

  data() {
    return {
      sectionlist: [],
      searchQuery: ''
    };
  },

  mounted() {
    this.loadSections();
  },

  computed: {
    filteredSections() {
      return this.sectionlist.filter(section => {
        return section.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
               section.description.toLowerCase().includes(this.searchQuery.toLowerCase());
      });
    }
  },

  methods: {
    ...mapActions(['logout']),

    async loadSections() {
      try {
        const access_token = localStorage.getItem('access_token');
        const response = await axios.get('http://127.0.0.1:5000/api/sections', {
          headers: {
            'Authorization': `Bearer ${access_token}`
          }
        });
        this.sectionlist = response.data;
      } catch (error) {
        console.error('Error loading sections:', error);
      }
    },

    async viewbooks(section) {
      this.$router.push(`/user-dashboard/section/${section.id}`);
    },

    ProvideUrl(cover_url) {
      return cover_url || noCover;
    },

    formatDate(date) {
      const options = { year: 'numeric', month: 'long', day: 'numeric' };
      return new Date(date).toLocaleDateString(undefined, options);
    }
  }
};
</script>

<style scoped>
.dashboard {
  font-family: 'Arial', sans-serif;
  margin: 0 auto;
  padding: 20px;
}

.dashboard-title {
  font-size: 2em;
  color: #333;
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
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-container {
  display: flex;
  flex-wrap: wrap;
  gap: 40px;
  justify-content: center;
}

.section-card {
  background-color: rgb(243, 211, 211);
  border-radius: 8px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  width: 400px;
  text-align: center;
}

.section-cover {
  width: 400px;
  height: 300px;
  border-radius: 8px 8px 0 0;
}

.section-title {
  margin: 0;
  font-size: 1.5em;
  color: #333;
}

.section-actions {
  margin-top: 15px;
}

.action-button {
  width: 40%;
  margin: 5px;
  padding: 10px 15px;
  background-color: #007BFF;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.action-button:hover {
  background-color: #0056b3;
}

.no-sections-message {
  text-align: center;
  font-size: 1.2em;
  color: #777;
}
</style>