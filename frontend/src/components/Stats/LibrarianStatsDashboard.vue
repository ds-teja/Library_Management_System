<template>
  <h1>Library Statistics</h1>
  <h1>Summary</h1>
  <p>Total Users - {{ summary['total_users'] }}</p>
  <p>Total Sections - {{ summary['total_sections'] }}</p>
  <p>Total Ebooks - {{ summary['total_ebooks'] }}</p>
  <div class="dashboard">
    <h2>New Additions over the past 6 months</h2>
    <div class="chart-container">
      <SummaryStatsChart></SummaryStatsChart>
    </div>
    <h2>Popular Sections over the past 6 months</h2>
      <div class="chart-container">
      <SectionStatsChart></SectionStatsChart>
    </div>
    <h2>Popular EBooks over the past 6 months</h2>
    <div class="chart-container">
      <BookStatsChart></BookStatsChart>
    </div>
  </div>
    
    
</template>

<script>
import SummaryStatsChart from './SummaryStatsChart.vue'
import SectionStatsChart from './SectionStatsChart.vue'
import BookStatsChart from './BookStatsChart.vue'
import axios from 'axios'

export default {
  data(){
    return {
      summary:{}
    }
  },
  components: {
    SummaryStatsChart,
    SectionStatsChart,
    BookStatsChart
  },

  mounted() {
    this.loadSummary()
  },

  methods:{
    async loadSummary(){
      try { 
        const access_token = localStorage.getItem('access_token')
        const response = await axios.get('http://127.0.0.1:5000/librarian/stats/summary',{
                    headers:{
                        'Authorization': `Bearer ${access_token}`
                    }
                });
        if (response && response.data) {
          this.summary = response.data;
        } else {
          console.error("No data received from the API.");
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    }
  }
}
</script>

<style>
.chart-container {
  flex-basis: 40%;
  padding: 15px;
  background-color: rgb(240, 238, 238);
  border-radius:5px;
  width:90vw;
  justify-content: center;
  margin:20px auto 20px auto;
}
</style>