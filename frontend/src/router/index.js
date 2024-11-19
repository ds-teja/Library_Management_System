import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LibrarianDashboard from '../views/LibrarianDashboard.vue'
import UserDashboard from '../views/UserDashboard.vue'
import ErrorPage from  '../views/Errorpage.vue'

import LibrarianLogin from '../components/Auth/LibrarianLogin.vue';
import UserLogin from '../components/Auth/UserLogin.vue';
import UserRegister from '../components/Auth/UserRegister.vue'

import AddSection from '../components/Section/AddSection.vue'
import UserAllSections from '../components/Section/UserAllSections.vue'

import AddBook from '../components/Book/AddBook.vue'
import ViewBook from '../components/Book/ViewBook.vue'
import EditBook from '../components/Book/EditBook.vue'
import LibrarianAllBooks from '../components/Book/LibrarianAllBooks.vue'
import UserAllBooks from '../components/Book/UserAllBooks.vue'
import UserBookshelves from '../components/Book/UserBookshelves.vue'
import BookPayment from '../components/Book/BookPayment.vue'
import KnowMore from '../components/Book/KnowMore.vue'

import LibrarianAllRequests from '../components/Request/LibrarianAllRequests.vue'
import UserAllRequests from '../components/Request/UserAllRequests.vue'
import UserSpecificRequests from '../components/Request/UserSpecificRequests.vue'
import BookSpecificRequests from '../components/Request/BookSpecificRequests.vue'

import MonitorUsers from '../components/User/MonitorUsers.vue'

import LibrarianStats from '../components/Stats/LibrarianStatsDashboard.vue'
import UserStats from '../components/Stats/UserStatsDashboard.vue'

import store from '../store/index.js'
const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: {requiresGuest:true}
  },
  {
    path: '/librarian-login',
    name: 'LibrarianLogin',
    component: LibrarianLogin,
    meta: {requiresGuest:true}
  },
  {
    path: '/librarian-dashboard',
    name: 'LibrarianDashboard',
    component:  LibrarianDashboard,
    meta: { requiresAuth: true, roles: ['librarian'] }
  }, 
  {
    path: '/librarian-dashboard/addsection',
    name: 'AddSection',
    component:  AddSection,
    meta: {requiresAuth:true, roles: ['librarian']}
  },
  {
    path: '/librarian-dashboard/addbook/:id?',
    name: 'AddBook',
    component: AddBook,
    props: route => ({ id: route.params.id || null }),
    meta: {requiresAuth:true, roles: ['librarian']}
  },
  {
    path: '/librarian-dashboard/editbook/:id',
    name: 'EditBook',
    component: EditBook,
    props: true,
    meta: {requiresAuth:true, roles: ['librarian']}
  },
  {
    path:'/librarian-dashboard/allbooks/:id?',
    name:'LibrarianAllBooks',
    component:LibrarianAllBooks,
    props: route => ({ id: route.params.id || null }),
    meta:{requiresAuth:true, roles: ['librarian']}
  },
  {
    path:'/librarian-dashboard/requests',
    name: 'LibrarianAllRequests',
    component: LibrarianAllRequests,
    meta: {requiresAuth:true, roles: ['librarian']}
  },
  {
    path:'/librarian-dashboard/users/requests/:id',
    name: 'UserSpecificRequests',
    component: UserSpecificRequests,
    props:true,
    meta: {requiresAuth:true, roles: ['librarian']}
  },
  {
    path:'/librarian-dashboard/books/requests/:id',
    name: 'BookSpecificRequests',
    component: BookSpecificRequests,
    props:true,
    meta: {requiresAuth:true, roles: ['librarian']}
  },
  {
    path:'/librarian-dashboard/users',
    name:'MonitorUsers',
    component:MonitorUsers,
    meta:{requiresAuth:true, roles: ['librarian']}
  },
  {
    path:'/librarian-dashboard/stats',
    name:'LibrarianStats',
    component:LibrarianStats,
    meta:{requiresAuth:true, roles:['librarian']}
  },
  {
    path: '/viewbook/:id',
    name: 'ViewBook',
    component: ViewBook,
    props: true,
    meta: {requiresAuth:true}
  },
  {
    path: '/book/details/:id',
    name:'KnowMore',
    component: KnowMore,
    props: true,
    meta:{requiresAuth:true}
  },
  {
    path: '/user-register',
    name: 'UserRegister',
    component:  UserRegister,
    meta: {requiresGuest:true}
  },
  {
    path: '/user-login',
    name: 'UserLogin',
    component: UserLogin,
    meta: {requiresGuest:true}
  },
  {
    path: '/user-dashboard',
    name: 'UserDashboard',
    component:  UserDashboard, 
    meta: { requiresAuth: true, roles: ['user'] }
  },
  {
    path: '/user-dashboard/requests',
    name: 'UserAllRequests',
    component: UserAllRequests,
    props: true,
    meta: {requiresAuth:true, roles: ['user'] }
  },
  {
    path:'/user-dashboard/sections',
    name:'UserAllSections',
    component: UserAllSections, 
    meta: {requiresAuth: true, roles: ['user'] }
  },
  {
    path:'/user-dashboard/section/:id?',
    name:'UserAllBooks',
    component: UserAllBooks,
    props: route => ({ id: route.params.id || null }),
    meta: {requiresAuth: true, roles: ['user'] }
  },
  {
    path:'/user-dashboard/payment/:id',
    name:'BookPayment',
    component:BookPayment,
    props:true,
    meta:{requiresAuth:true,roles:['user']}
  },
  {
    path:'/users/stats/:id?',
    name:'UserStats',
    component:UserStats,
    props: route => ({ id: route.params.id || null }),
    meta:{requiresAuth:true, roles: ['user','librarian'] }
  },
  {
    path:'/user-dashboard/bookshelves',
    name:'UserBookshelves',
    component:UserBookshelves,
    meta:{requiresAuth:true, roles: ['user'] }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'Error',
    component: ErrorPage
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Navigation guard to check authentication and role
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    if (!store.getters.isAuthenticated) {
      next('/');
    } 
    else {
      const userRole = store.getters.userRole;
      if (to.meta.roles && !to.meta.roles.includes(userRole)) {
        next('/');
      } else {
        next();
      }
    }
  } 
  else if (to.meta.requiresGuest && store.getters.isAuthenticated) {
    if (store.getters.userRole=='librarian'){
      next('/librarian-dashboard');
    }
    else if (store.getters.userRole=='user') {
      next('/user-dashboard');
    } else {
      next('/');
    }
  } 
  else {
    next();
  }
});

export default router;
