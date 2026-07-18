<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-900 py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
    <!-- Decorative background elements -->
    <div class="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
      <div class="absolute top-[-10%] left-[-10%] w-96 h-96 bg-indigo-600 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div class="absolute top-[20%] right-[-10%] w-96 h-96 bg-purple-600 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
      <div class="absolute bottom-[-20%] left-[20%] w-96 h-96 bg-pink-600 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
    </div>

    <div class="max-w-md w-full space-y-8 bg-gray-800/80 backdrop-blur-xl p-10 rounded-2xl shadow-2xl border border-gray-700/50 z-10 transform transition-all hover:scale-[1.01]">
      <div class="text-center">
        <div class="flex justify-center mb-4">
          <img src="/logo.png" alt="KeepMeUpdated Logo" class="w-20 h-20 object-contain drop-shadow-lg" />
        </div>
        <h1 class="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400 mb-2 tracking-tight">KeepMeUpdated</h1>
        <h2 class="text-xl text-gray-300 font-medium">Create an account</h2>
        <p class="text-sm text-gray-400 mt-2">Join us to automate your notifications</p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div class="space-y-4">
          <div>
            <label for="email-address" class="block text-sm font-medium text-gray-300 mb-1">Email address</label>
            <input id="email-address" name="email" type="email" autocomplete="email" required v-model="email"
                   class="appearance-none relative block w-full px-4 py-3 border border-gray-600 bg-gray-700/50 placeholder-gray-400 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all sm:text-sm" placeholder="you@example.com">
          </div>
          <div>
            <label for="password" class="block text-sm font-medium text-gray-300 mb-1">Password</label>
            <input id="password" name="password" type="password" required v-model="password"
                   class="appearance-none relative block w-full px-4 py-3 border border-gray-600 bg-gray-700/50 placeholder-gray-400 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all sm:text-sm" placeholder="••••••••">
          </div>
        </div>

        <div v-if="errorMessage" class="text-red-400 text-sm text-center bg-red-900/30 py-2 rounded border border-red-800/50">
          {{ errorMessage }}
        </div>

        <div>
          <button type="submit" :disabled="isLoading"
                  class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-bold rounded-lg text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-indigo-500 transition-all shadow-lg transform hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed">
            <span v-if="isLoading">Registering...</span>
            <span v-else>Register</span>
          </button>
        </div>
      </form>

      <div class="text-center mt-6">
        <p class="text-sm text-gray-400">
          Already have an account? 
          <router-link to="/login" class="font-medium text-indigo-400 hover:text-indigo-300 transition-colors">Sign in</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const email = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)
const router = useRouter()

const handleRegister = async () => {
  errorMessage.value = ''
  isLoading.value = true
  try {
    await axios.post('/api/auth/register', {
      email: email.value,
      password: password.value
    })
    router.push('/login')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Failed to register. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style>
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}
.animate-blob {
  animation: blob 7s infinite;
}
.animation-delay-2000 {
  animation-delay: 2s;
}
.animation-delay-4000 {
  animation-delay: 4s;
}
</style>
