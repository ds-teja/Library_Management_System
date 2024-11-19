<template>
    <div>
      <Bar v-if="loaded" :data="chartData" :options="chartOptions"  :height="120" />
    </div>
  </template>
  
<script>
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
import axios from 'axios';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)
  
export default {
components: {
    Bar
},
data() {
    return {
        loaded:false,
        chartData: {
            labels: [],
            datasets: [
            {
                label: 'Number of Requests',
                backgroundColor:'#8F3E6E',
                data: [],
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
            },
            ],
        },
        chartOptions: {
            responsive: true,
            plugins: {
            title: {
                display: true,
                text: 'Popular Ebooks for the Past 6 Months'
            }
            }
        }
    };
},
mounted() {
    this.fetchPopularEbooks();
},
methods: {
    fetchPopularEbooks() {
        const access_token = localStorage.getItem('access_token')
        axios.get(`http://127.0.0.1:5000/librarian/stats/ebooks`,{
                    headers:{
                        'Authorization': `Bearer ${access_token}`
                    }
                }).then((response) => {
        const sections = response.data;
        this.chartData.labels = sections.map((section) => section.name);
        this.chartData.datasets[0].data = sections.map((section) => section.request_count);
        this.chartData.datasets[1].data = sections.map((section) => section.pending);
        this.chartData.datasets[2].data = sections.map((section) => section.declined);
        this.chartData.datasets[3].data = sections.map((section) => section.withdrawn);
        this.chartData.datasets[4].data = sections.map((section) => section.approved);
        this.chartData.datasets[5].data = sections.map((section) => section.returned);
        this.chartData.datasets[6].data = sections.map((section) => section.revoked);
        this.loaded = true;
        })
        .catch((error) => {
        console.error('Error fetching popular sections:', error);
        });
    },
},

};
</script>
  