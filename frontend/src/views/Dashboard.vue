<template>
  <div class="min-h-screen bg-gray-900 text-white pb-12">
    <header class="bg-gray-800 shadow border-b border-gray-700">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
        <div class="flex items-center space-x-8">
          <h1 class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">KeepMeUpdated</h1>
          <nav class="hidden md:flex space-x-4">
            <router-link to="/" class="text-white bg-gray-900 px-3 py-2 rounded-md text-sm font-medium">Dashboard</router-link>
            <router-link to="/settings" class="text-gray-400 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">Settings</router-link>
          </nav>
        </div>
        <button @click="logout" class="text-gray-300 hover:text-white transition-colors">Logout</button>
      </div>
    </header>
    
    <main class="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8 space-y-8">
      <!-- Notifications Section -->
      <section class="bg-gray-800 rounded-xl p-6 shadow-2xl border border-gray-700">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold">Scheduled Notifications</h2>
          <button @click="openAddNotification" class="bg-indigo-600 hover:bg-indigo-500 text-white py-2 px-4 rounded-lg shadow-md transition-all transform hover:scale-105">+ Create Notification</button>
        </div>
        <div v-if="notifications.length === 0" class="text-gray-400 text-center py-8 bg-gray-700/30 rounded-lg border border-dashed border-gray-600">No notifications scheduled.</div>
        <ul class="space-y-4">
          <li v-for="notif in notifications" :key="notif.id" class="bg-gray-700 p-5 rounded-lg border border-gray-600 flex flex-col sm:flex-row justify-between sm:items-center group">
            <div class="mb-4 sm:mb-0">
              <div class="flex items-center space-x-3 mb-1">
                <span class="font-bold text-xl">{{ notif.title }}</span>
                <span class="text-xs bg-gray-600 text-gray-200 px-2 py-1 rounded">{{ notif.schedule_type }}</span>
                <span class="text-xs text-gray-400">Channel ID: {{ notif.channel_id }}</span>
              </div>
              <p class="text-gray-300 text-sm mb-2 line-clamp-2">{{ notif.parameters?.body || notif.payload }}</p>
              <div class="text-xs text-indigo-300">
                Next run: {{ notif.next_run_at ? new Date(notif.next_run_at + 'Z').toLocaleString() : 'Not scheduled' }}
              </div>
            </div>
            <div class="flex items-center space-x-4">
              <button @click="confirmDeleteNotification(notif)" class="text-gray-400 hover:text-red-400 transition-colors text-sm">Delete</button>
              <button @click="toggleNotification(notif)" 
                      :class="notif.is_active ? 'bg-red-500/20 text-red-400 hover:bg-red-500/40 border-red-500/50' : 'bg-green-500/20 text-green-400 hover:bg-green-500/40 border-green-500/50'" 
                      class="px-4 py-2 rounded-lg text-sm font-medium border transition-all">
                {{ notif.is_active ? 'Deactivate' : 'Activate' }}
              </button>
            </div>
          </li>
        </ul>
      </section>
    </main>

    <!-- Skip/Deactivate Modal -->
    <div v-if="showSkipModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
      <div class="bg-gray-800 p-8 rounded-2xl max-w-md w-full border border-gray-600 shadow-2xl transform transition-all">
        <div class="flex items-center justify-center w-12 h-12 mx-auto bg-yellow-500/20 rounded-full mb-4">
          <Settings class="w-6 h-6 text-yellow-500" />
        </div>
        <h3 class="text-2xl font-bold mb-2 text-center text-white">Deactivate Notification</h3>
        <p class="mb-8 text-gray-300 text-center text-sm leading-relaxed">
          This is a repeating notification. Do you want to skip just the next scheduled instance, or deactivate all future instances completely?
        </p>
        <div class="flex flex-col sm:flex-row justify-center gap-3">
          <button @click="showSkipModal = false" class="px-5 py-2.5 text-gray-300 hover:text-white bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-sm font-medium">Cancel</button>
          <button @click="handleSkipNext" class="px-5 py-2.5 bg-yellow-600 hover:bg-yellow-500 text-white rounded-lg transition-colors text-sm font-medium shadow-md">Skip Next</button>
          <button @click="handleDeactivateAll" class="px-5 py-2.5 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors text-sm font-medium shadow-md">Deactivate All</button>
        </div>
      </div>
    </div>

    <div v-if="showConfirmModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
      <div class="bg-gray-800 p-8 rounded-2xl max-w-sm w-full border border-gray-600 shadow-2xl">
        <h3 class="text-xl font-bold mb-4 text-white">{{ confirmModalState.title }}</h3>
        <p class="mb-8 text-gray-300 text-sm leading-relaxed">{{ confirmModalState.message }}</p>
        <div class="flex justify-end gap-3">
          <button @click="showConfirmModal = false" class="px-4 py-2 text-gray-300 hover:text-white bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-sm">Cancel</button>
          <button @click="confirmModalState.onConfirm" class="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors text-sm shadow-md">Delete</button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toast.show" class="fixed bottom-4 right-4 max-w-sm w-full p-4 rounded-lg shadow-xl z-[100] border transition-all transform duration-300 ease-in-out translate-y-0" :class="toast.type === 'success' ? 'bg-green-800/90 border-green-600' : 'bg-red-800/90 border-red-600'">
      <div class="flex items-center justify-between">
        <span class="text-sm font-medium text-white">{{ toast.message }}</span>
        <button @click="toast.show = false" class="text-white/70 hover:text-white">&times;</button>
      </div>
    </div>

    <!-- Notification Modal -->
    <div v-if="showNotificationModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-gray-800 p-8 rounded-2xl max-w-lg w-full border border-gray-600 shadow-2xl overflow-y-auto max-h-[90vh]">
        <h3 class="text-2xl font-bold mb-6 text-white">Create Notification</h3>
        <form @submit.prevent="saveNotification" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1">Target Channel</label>
            <select v-model="notificationForm.channel_id" required class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option disabled value="">Select a channel...</option>
              <option v-for="channel in channels" :key="channel.id" :value="channel.id">{{ channel.name }} ({{ channel.plugin_id }})</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1">Title</label>
            <input v-model="notificationForm.title" type="text" required placeholder="Notification Title" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
          </div>
          <div v-if="!selectedChannelPluginSchema || Object.keys(selectedChannelPluginSchema.properties || {}).length === 0">
            <label class="block text-sm font-medium text-gray-300 mb-1">Message Payload</label>
            <textarea v-model="notificationForm.payload" rows="3" placeholder="Message content..." class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"></textarea>
          </div>
          
          <div v-if="selectedChannelPluginSchema && Object.keys(selectedChannelPluginSchema.properties || {}).length > 0" class="space-y-4 mt-6">
            <h4 class="text-lg font-semibold border-b border-gray-700 pb-2">Message Details</h4>
            <div v-for="(field, key) in selectedChannelPluginSchema.properties" :key="key">
              <label class="block text-sm font-medium text-gray-300 mb-1">{{ field.title || key }} <span v-if="selectedChannelPluginSchema.required?.includes(key)" class="text-red-400">*</span></label>
              <textarea v-if="key === 'body' || (field.type === 'string' && field.format === 'textarea')" v-model="notificationForm.parameters[key]" :required="selectedChannelPluginSchema.required?.includes(key)" rows="3" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"></textarea>
              <input v-else-if="field.type === 'string' && field.format !== 'password'" v-model="notificationForm.parameters[key]" type="text" :required="selectedChannelPluginSchema.required?.includes(key)" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <input v-else-if="field.type === 'string' && field.format === 'password'" v-model="notificationForm.parameters[key]" type="password" :required="selectedChannelPluginSchema.required?.includes(key)" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <input v-else-if="field.type === 'integer'" v-model.number="notificationForm.parameters[key]" type="number" :required="selectedChannelPluginSchema.required?.includes(key)" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <div v-else-if="field.type === 'boolean'" class="flex items-center">
                <input v-model="notificationForm.parameters[key]" type="checkbox" class="w-4 h-4 text-indigo-600 bg-gray-700 border-gray-600 rounded focus:ring-indigo-500 focus:ring-2">
                <span class="ml-2 text-sm text-gray-300">Enable</span>
              </div>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-1">Schedule Type</label>
              <select v-model="notificationForm.schedule_type" required class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="specific_time">Specific Time</option>
                <option value="cron">Cron</option>
                <option value="interval">Interval</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-1">Schedule Expression</label>
              
              <!-- Specific Time -->
              <div v-if="notificationForm.schedule_type === 'specific_time'" class="flex space-x-2">
                <input v-model="specificTimeInputs.date" type="date" required class="w-1/2 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <div class="flex space-x-1 w-1/2">
                  <select v-model="specificTimeInputs.hour" required class="w-full bg-gray-700 border border-gray-600 rounded-lg px-2 py-2 text-center text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option disabled value="">HH</option>
                    <option v-for="h in 24" :key="h-1" :value="String(h-1).padStart(2, '0')">{{ String(h-1).padStart(2, '0') }}</option>
                  </select>
                  <span class="text-gray-300 self-center font-bold">:</span>
                  <select v-model="specificTimeInputs.minute" required class="w-full bg-gray-700 border border-gray-600 rounded-lg px-2 py-2 text-center text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option disabled value="">MM</option>
                    <option v-for="m in 60" :key="m-1" :value="String(m-1).padStart(2, '0')">{{ String(m-1).padStart(2, '0') }}</option>
                  </select>
                </div>
              </div>
              
              <!-- Interval -->
              <div v-else-if="notificationForm.schedule_type === 'interval'" class="flex space-x-2">
                <input v-model.number="intervalInputs.value" type="number" min="1" required class="w-1/3 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <select v-model="intervalInputs.unit" class="w-2/3 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option value="minutes">Minutes</option>
                  <option value="hours">Hours</option>
                  <option value="days">Days</option>
                </select>
              </div>

              <!-- Cron -->
              <div v-else-if="notificationForm.schedule_type === 'cron'" class="flex space-x-1">
                <input v-model="cronInputs.min" type="text" placeholder="Min" title="Minute" required class="w-1/5 bg-gray-700 border border-gray-600 rounded-lg px-1 py-2 text-center text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <input v-model="cronInputs.hour" type="text" placeholder="Hr" title="Hour" required class="w-1/5 bg-gray-700 border border-gray-600 rounded-lg px-1 py-2 text-center text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <input v-model="cronInputs.dom" type="text" placeholder="DOM" title="Day of Month" required class="w-1/5 bg-gray-700 border border-gray-600 rounded-lg px-1 py-2 text-center text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <input v-model="cronInputs.mon" type="text" placeholder="Mon" title="Month" required class="w-1/5 bg-gray-700 border border-gray-600 rounded-lg px-1 py-2 text-center text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <input v-model="cronInputs.dow" type="text" placeholder="DOW" title="Day of Week" required class="w-1/5 bg-gray-700 border border-gray-600 rounded-lg px-1 py-2 text-center text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              </div>
            </div>
          </div>
          
          <div class="flex items-center mt-2">
             <input v-model="notificationForm.is_active" type="checkbox" class="w-4 h-4 text-indigo-600 bg-gray-700 border-gray-600 rounded focus:ring-indigo-500 focus:ring-2">
             <span class="ml-2 text-sm text-gray-300">Active Immediately</span>
          </div>
          
          <div class="flex justify-end gap-3 mt-8">
            <button type="button" @click="showNotificationModal = false" class="px-5 py-2 text-gray-300 hover:text-white bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
            <button type="submit" class="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors shadow-md">Create</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Settings } from 'lucide-vue-next'

const authStore = useAuthStore()
const router = useRouter()

const channels = ref([])
const notifications = ref([])
const availablePlugins = ref([])
const repositories = ref([])

const showSkipModal = ref(false)
const selectedNotification = ref(null)

const showConfirmModal = ref(false)
const confirmModalState = ref({ title: '', message: '', onConfirm: null })

const toast = ref({ show: false, message: '', type: 'success' })
const showToast = (message, type = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => toast.value.show = false, 3000)
}

const selectedChannelPluginSchema = computed(() => {
  if (!notificationForm.value.channel_id) return null
  const channel = channels.value.find(c => c.id === notificationForm.value.channel_id)
  if (!channel) return null
  const plugin = availablePlugins.value.find(p => p.id === channel.plugin_id)
  return plugin ? plugin.notification_schema : null
})

watch(() => notificationForm.value.channel_id, (newChannelId) => {
  if (newChannelId) {
    notificationForm.value.parameters = {}
  }
})

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const getHeaders = () => ({ Authorization: `Bearer ${authStore.token}` })

const fetchDashboardData = async () => {
  try {
    const [channelsRes, notifsRes, pluginsRes, reposRes] = await Promise.all([
      axios.get('http://localhost:8000/api/channels', { headers: getHeaders() }),
      axios.get('http://localhost:8000/api/notifications', { headers: getHeaders() }),
      axios.get('http://localhost:8000/api/channels/plugins', { headers: getHeaders() }),
      axios.get('http://localhost:8000/api/repositories', { headers: getHeaders() })
    ])
    
    channels.value = channelsRes.data
    notifications.value = notifsRes.data
    availablePlugins.value = pluginsRes.data
  } catch (error) {
    if (error.response?.status === 401) {
      logout()
    } else {
      showToast('Failed to load dashboard data', 'error')
    }
  }
}

onMounted(() => {
  fetchDashboardData()
})

const toggleNotification = async (notif) => {
  if (notif.is_active && (notif.schedule_type === 'cron' || notif.schedule_type === 'interval')) {
    selectedNotification.value = notif
    showSkipModal.value = true
  } else {
    try {
      await axios.put(`http://localhost:8000/api/notifications/${notif.id}`, { is_active: !notif.is_active }, { headers: getHeaders() })
      await fetchDashboardData()
    } catch(e) { 
      showToast('Failed to toggle notification', 'error') 
    }
  }
}

const confirmDeleteNotification = (notif) => {
  confirmModalState.value = {
    title: 'Delete Notification',
    message: `Are you sure you want to delete ${notif.title}?`,
    onConfirm: async () => {
      try {
        await axios.delete(`http://localhost:8000/api/notifications/${notif.id}`, { headers: getHeaders() })
        showConfirmModal.value = false
        await fetchDashboardData()
        showToast('Notification deleted')
      } catch(e) {
        showToast('Failed to delete notification', 'error')
      }
    }
  }
  showConfirmModal.value = true
}

const handleSkipNext = () => {
  showSkipModal.value = false
  showToast(`Skipped next instance for: ${selectedNotification.value.title}`)
}

const handleDeactivateAll = async () => {
  try {
    await axios.put(`http://localhost:8000/api/notifications/${selectedNotification.value.id}`, { is_active: false }, { headers: getHeaders() })
    showSkipModal.value = false
    await fetchDashboardData()
    showToast('Deactivated completely')
  } catch(e) { 
    showToast('Failed to deactivate notification', 'error') 
  }
}

const openAddNotification = () => {
  notificationForm.value = { channel_id: '', title: '', payload: '', schedule_type: 'specific_time', schedule_expr: '', parameters: {}, is_active: true }
  
  const now = new Date()
  const offset = now.getTimezoneOffset() * 60000
  const localDate = new Date(now.getTime() - offset + 3600000).toISOString().slice(0, 16)
  
  const [d, t] = localDate.split('T')
  const [hh, mm] = t.split(':')
  specificTimeInputs.value = { date: d, hour: hh, minute: mm }
  intervalInputs.value = { value: 10, unit: 'minutes' }
  cronInputs.value = { min: '*', hour: '*', dom: '*', mon: '*', dow: '*' }
  
  showNotificationModal.value = true
}

const saveNotification = async () => {
  try {
    const payload = { ...notificationForm.value }
    
    if (payload.schedule_type === 'specific_time') {
      const { date, hour, minute } = specificTimeInputs.value
      if (date && hour && minute) {
        payload.schedule_expr = `${date}T${hour}:${minute}`
        const localDate = new Date(payload.schedule_expr)
        if (!isNaN(localDate)) {
          payload.schedule_expr = localDate.toISOString()
        }
      }
    } else if (payload.schedule_type === 'interval') {
      payload.schedule_expr = `${intervalInputs.value.value} ${intervalInputs.value.unit}`
    } else if (payload.schedule_type === 'cron') {
      const { min, hour, dom, mon, dow } = cronInputs.value
      payload.schedule_expr = `${min} ${hour} ${dom} ${mon} ${dow}`
    }
    
    await axios.post('http://localhost:8000/api/notifications', payload, { headers: getHeaders() })
    showNotificationModal.value = false
    await fetchDashboardData()
    showToast('Notification created successfully')
  } catch(e) {
    showToast('Failed to save notification', 'error')
  }
}
</script>
