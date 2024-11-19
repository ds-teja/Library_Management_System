<template>
  <div style="display:flex">
    <div class="bar-container">
      <Bar v-if="loaded" :data="UsersChartData" :options="UsersChartOptions" :height="250"/>
    </div>
    <div class="bar-container">
      <Bar v-if="loaded" :data="SectionsChartData" :options="SectionsChartOptions" :height="250"/>
    </div>
    <div class="bar-container">
      <Bar v-if="loaded" :data="BooksChartData" :options="BooksChartOptions" :height="250"/>
    </div>
  </div>
</template>

<script>
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)
import axios from 'axios'

export default {
  name: 'BarChart',

  components:{
    Bar,
  },

  data() {
    return {
      loaded: false,
      UsersChartData: {
        labels: [],
        datasets: [
          {
            label: 'New Users',
            backgroundColor: '#f87979',
            data: []
          }
        ]
      },
      SectionsChartData: {
        labels: [],
        datasets: [
          {
            label: 'New Sections',
            backgroundColor: '#7cbf79',
            data: []
          }
        ]
      },
      BooksChartData: {
        labels: [],
        datasets: [
          {
            label: 'New Books',
            backgroundColor: '#79a4f8',
            data: []
          }
        ]
      },
      UsersChartOptions: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Monthly New Users for the Past 6 Months'
          }
        }
      },
      SectionsChartOptions: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Monthly New Sections for the Past 6 Months'
          }
        }
      },
      BooksChartOptions: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Monthly New Books for the Past 6 Months'
          }
        }
      }
    }
  },

  async mounted() {
    await this.fetchData();
  },

  methods: {
    async fetchData() {
      try {
        const access_token = localStorage.getItem('access_token');
        const response = await axios.get('http://127.0.0.1:5000/librarian/stats/new',{
          headers:{
            'Authorization':`Bearer ${access_token}`
          }
        });
        if (response && response.data) {
          this.UsersChartData.labels = response.data.user_labels;
          this.UsersChartData.datasets[0].data = response.data.new_users;

          this.SectionsChartData.labels = response.data.section_labels;
          this.SectionsChartData.datasets[0].data = response.data.new_sections;

          this.BooksChartData.labels = response.data.book_labels;
          this.BooksChartData.datasets[0].data = response.data.new_books;

          this.loaded = true;
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

<style scoped>
.bar-container{
  flex-basis:30%;padding:10px;margin:10px;
}
</style>