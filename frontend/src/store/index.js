import { createStore } from 'vuex';
import router from '../router';
import { jwtDecode } from 'jwt-decode';
import axios from 'axios';

export default createStore({
  state: {
    token: localStorage.getItem('access_token') || null,
  },

  getters: {
    isAuthenticated: state => !!state.token,
    userRole: state => {
      if (state.token) {
        const decoded = jwtDecode(state.token);
        return decoded.sub.role;
      }
      return null;
    },
    userId: state => {
      if (state.token) {
        const decoded = jwtDecode(state.token);
        return decoded.sub.id;
      }
      return null;
    }, 
  },

  mutations: {
    setToken(state, token) {
      state.token = token;
      localStorage.setItem('access_token', token);
    },

    removeToken(state) {
      state.token = '';
      localStorage.removeItem('access_token');
    }
  },

  actions: {
    async login({ commit }, { token }) {
      commit('setToken', token);
    },

    async logout({ commit, state }) {
      if (!state.token) {
        console.error('No token found in state. Logout action aborted.');
        return;
      } else{
        await axios.post('http://127.0.0.1:5000/api/auth/logout',null,{
          headers:{
            'Authorization':`Bearer ${state.token}`
          }
        }).then(() => {
          commit('removeToken');
          router.push('/');
        }).catch(error => {
          console.error('Logout failed:', error);
        });
      }
    }
  }

});