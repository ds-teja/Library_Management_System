<template>
    <div class="dashboard">  
    <div style="display:flex;width:95%; justify-content: space-between;align-items:center;margin:auto auto;">
      <h2 style="margin-left:40vw">All Sections</h2>
       <div style="display:flex;gap:10px">
        <button @click="addsection" class="add-button">Add New Section</button>
        <button @click="addbook" class="add-button">Add New Book to any existing section</button>
      </div>
    </div>
    
    <div v-if="filteredSections.length > 0">
      <div style="width:95%;margin:auto;">
        <input type="text" v-model="searchQuery" placeholder="Search sections..." class="search-input" />
      </div>
      
      <div class="section-container">
        <div v-for="section in filteredSections" :key="section.id" class="section-card">
          <img :src="ProvideUrl(section.cover_url)" alt="Section Cover" class="section-cover">
          <h3 class="section-title">{{ section.name }}</h3>
          <p><strong>Created Date:</strong> {{ formatDate(section.created_date) }}</p>
          <p><strong>Description:</strong> {{ section.description }}</p>
          <div class="section-actions">
            <button @click="changeEditModal(section.id)" class="action-button"><strong>Edit Section</strong></button>
            <button @click="confirmDeleteSection(section.id)" class="action-button delete-button"><strong>Delete Section</strong></button>
            <button @click="addbookToSection(section)" class="action-button"><strong>Add Book</strong></button>
            <button @click="viewbooks(section)" class="action-button"><strong>View Books</strong></button>
          </div>
      </div>
      </div>
      
    </div>
    <div v-else>
      <p class="no-sections-message">No sections available.</p>
    </div>
  </div>

  <!-- Modal for Editing Section -->
  <div v-if="showEditModal" class="modal">
    <div class="modal-content">
      <span class="close" @click="closeModal">&times;</span>
      <h1>Editing Section {{ this.section_name }}</h1>
      <form @submit.prevent="editSection(this.newSection)">
        <div>
          <label for="name">Name:</label>
          <input type="text" v-model="this.newSection.name" id="name" required>
        </div>
        <div>
          <label for="description">Description:</label>
          <input type="text" v-model="this.newSection.description" id="description" required>
        </div>
        <div>
            <label for="cover">Change Section Cover:</label>
            <input type="file" @change="handleCoverUpload" id="cover">
        </div>
        <button type="submit">Edit Section</button>
      </form>
    </div>
  </div>

  <!-- Modal for deletion confirmation -->
  <div v-if="showDeleteModal" class="modal">
    <div class="modal-content">
      <span class="close" @click="closeModal">&times;</span>
      <p><strong>Choose the preferred type of deletion</strong>:</p> 
      <button class="modal-button" @click="deleteSection(selectedSectionId, true)"><strong>Delete the Section and also the books of the section</strong>.</button>
      <button class="modal-button" @click="promptMoveBooks()"><strong>Move Books to another section and then Delete the section.</strong></button>
      <button @click="closeModal">Cancel</button>
    </div>
  </div>

  <!-- Modal for selecting new section to move books -->
  <div v-if="showMoveBooksModal" class="modal">
    <div class="modal-content">
      <span class="close" @click="closeModal">&times;</span>
      <p><strong>Then please select a section to which you want to move the books of this section:</strong></p>
      <select v-model="newSectionId">
        <option value="" disabled selected>Select any Section</option>
        <option v-for="section in optionsectionlist" :key="section.id" :value="section.id">{{ section.name }}</option>
      </select>
      <button  class="modal-button" @click="deleteSection(selectedSectionId, false, newSectionId)"><strong>Move Books and Delete Section</strong></button>
    </div>
  </div>
</template>

<script>
import {mapActions} from 'vuex';
import axios from 'axios';
import noCover from '@/assets/no-image-available.jpg';

export default {
  name: 'LibrarianAllSections',

  data() {
    return {
      sectionlist:[],
      showEditModal: false,
      showDeleteModal: false,
      showMoveBooksModal: false,
      selectedSectionId: null,
      newSectionId: '',
      newSection: {},
      section_name:'',
      searchQuery: ''
    }
  },

  computed:{
    filteredSections() {
      return this.sectionlist.filter(section => {
        return section.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
               section.description.toLowerCase().includes(this.searchQuery.toLowerCase());
      });
    },
    optionsectionlist(){
      return this.sectionlist.filter(section => section.id !== this.selectedSectionId);
    }
  },

  mounted() {
    this.loadSections();
  },

  methods: {
    ...mapActions(['logout']),

    async addbookToSection(section) {
      this.$router.push(`/librarian-dashboard/addbook/${section.id}`)
    },

    async addbook() {
      this.$router.push(`/librarian-dashboard/addbook`)
    },
    
    async viewbooks(section) {
      this.$router.push(`/librarian-dashboard/allbooks/${section.id}`)
    },

    async addsection() {
      this.$router.push('/librarian-dashboard/addsection')
    },

    async editSection(section){
        try {
            const formData = new FormData();
            formData.append('id', section.id);
            formData.append('name', section.name);
            formData.append('description', section.description);
            formData.append('cover',section.cover);
            const access_token = localStorage.getItem('access_token')
            await axios.put(`http://127.0.0.1:5000/api/sections`, formData,
                {
                    headers:{
                        'Authorization': `Bearer ${access_token}`
                    }
                });
            alert("Section Updated Successfuly!");
            this.$router.push('/');
        }  catch (error) {
            alert("Error");
            console.error('Error Updating section:', error);
        }
    },

    handleCoverUpload(event){
      this.newSection.cover = event.target.files[0];
    },

    async loadSections() {
      try {
        const access_token = localStorage.getItem('access_token')
        const response = await axios.get('http://127.0.0.1:5000/api/sections',
            {
                headers:{
                    'Authorization': `Bearer ${access_token}`
                }
            });
        this.sectionlist = response.data;
      } catch (error) {
        console.error('Error loading sections:', error);
      }
    },

    confirmDeleteSection(sectionId) {
      this.selectedSectionId = sectionId;
      this.showDeleteModal = true;
    },

    closeModal() {
      this.showDeleteModal = false;
      this.showMoveBooksModal = false;
      this.showEditModal = false;
      this.selectedSectionId = null;
      this.newSectionId = '';
    },

    async deleteSection(sectionId, deleteBooks, newSectionId = null) {
      this.closeModal();
      if (!deleteBooks && !newSectionId) {
        this.showMoveBooksModal = true;
        return;
      }

      try {
        const access_token = localStorage.getItem('access_token');
        const response = await axios.delete(`http://127.0.0.1:5000/api/sections/${sectionId}`, {
          headers: {
            Authorization: `Bearer ${access_token}`
          },
          params: {
            delete_books: deleteBooks,
            new_section_id: newSectionId
          }
        });

        if (response.status === 200) {
          alert('Section deleted successfully!');
          this.loadSections(); // Reload sections after deletion
        }
      } catch (error) {
        console.error('Error deleting section:', error);
      }
    },

    promptMoveBooks() {
      this.showDeleteModal = false;
      this.showMoveBooksModal = true;
    },

    changeEditModal(section_id){
      this.newSection = this.sectionlist.find(section=>section.id==section_id);
      this.section_name = this.newSection.name;
      this.showEditModal = true;
    },

    formatDate(date) {
      const options = { year: 'numeric', month: 'long', day: 'numeric' };
      return new Date(date).toLocaleDateString(undefined, options);
    },

    ProvideUrl(cover_url){
      if(cover_url==''){
        return noCover;
      }else{
        return cover_url;
      }
    },
  },
}
</script>


<style scoped>
.dashboard {
  font-family: 'Arial', sans-serif;
  padding: 20px;
}

.dashboard-title {
  font-size: 2em;
  color: #333;
  text-align: center;
}

.search-input {
  margin: 0 auto 20px auto;
  padding: 10px;
  display:block;
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
  width:40%;
  margin: 5px;
  padding: 10px 15px;
  background-color: #636464;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.action-button:hover {
  background-color: #0056b3;
}

.delete-button:hover {
  background-color: #c82333;
}

.no-sections-message {
  text-align: center;
  color: #777;
  font-size: 1.2em;
}

.modal {
  display: block; 
  position: fixed; 
  z-index: 1; 
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  border-radius:10px;
  background-color: rgb(0,0,0); 
  background-color: rgba(0,0,0,0.4); 
}

.modal-content {
  background-color: #fbd2ff;
  margin: 15% auto auto auto; 
  padding: 20px;
  border: 1px solid #888;
  width: 80%; 
  display:flex;
  flex-direction:column;
  gap:20px;
  align-items: center;
}

.modal-button {
  color:white;
  background-color: #0056b3;
  border-radius:10px;
  height:30px;
  width:50%;
  font-size:17px;
}

.close {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
}

.close:hover,
.close:focus {
  color: black;
  text-decoration: none;
  cursor: pointer;
}

form {
  margin-bottom: 32px;
}
form div {
  margin-bottom: 16px;
}
label {
  display: block;
  margin-bottom: 8px;
}
input[type="text"],
input[type="date"] {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}
</style>