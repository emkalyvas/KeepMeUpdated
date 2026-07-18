<template>
  <div class="min-h-screen bg-gray-900 text-white pb-12">
    <header class="bg-gray-800 shadow border-b border-gray-700">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
        <div class="flex items-center space-x-8">
          <div class="flex items-center space-x-3">
            <img src="/logo.png" alt="KeepMeUpdated Logo" class="w-14 h-14 object-contain drop-shadow-md" />
            <h1 class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">KeepMeUpdated</h1>
          </div>
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
                Next run: {{ notif.next_run_at ? new Date(notif.next_run_at + 'Z').toLocaleString() : (notif.is_active ? 'Never' : 'Not scheduled') }}
              </div>
            </div>
            <div class="flex items-center space-x-4">
              <button @click="openEditNotification(notif)" class="text-gray-400 hover:text-indigo-400 transition-colors text-sm">Edit</button>
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
      <div class="bg-gray-800 p-8 pt-6 pb-6 rounded-2xl max-w-5xl w-full border border-gray-600 shadow-2xl flex flex-col max-h-[90vh] overflow-hidden">
        
        <h3 class="text-2xl font-bold mb-6 text-white shrink-0">{{ isEditing ? 'Edit Notification' : 'Create Notification' }}</h3>
        
        <div class="flex-1 flex flex-col md:flex-row gap-8 overflow-hidden min-h-0">
          <!-- Form Column -->
          <div class="flex-1 overflow-y-auto pr-4 custom-scrollbar">
            <form id="notification-form" @submit.prevent="saveNotification" class="space-y-4 pb-4">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1">Target Channel</label>
            <select v-model="notificationForm.channel_id" @change="notificationForm.parameters = {}" required class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
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
              <select v-else-if="field.enum" v-model="notificationForm.parameters[key]" :required="selectedChannelPluginSchema.required?.includes(key)" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option v-for="option in field.enum" :key="option" :value="option">{{ option }}</option>
              </select>
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
          
          <div v-if="notificationForm.schedule_type !== 'specific_time'" class="mt-4">
            <label class="block text-sm font-medium text-gray-300 mb-1">Start Time (Optional)</label>
            <input v-model="notificationForm.start_time" type="datetime-local" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <p class="text-xs text-gray-400 mt-1">The schedule will begin from this time. Leave empty to start immediately.</p>
          </div>
          
          <div class="flex items-center mt-2">
             <input v-model="notificationForm.is_active" type="checkbox" class="w-4 h-4 text-indigo-600 bg-gray-700 border-gray-600 rounded focus:ring-indigo-500 focus:ring-2">
             <span class="ml-2 text-sm text-gray-300">Active Immediately</span>
          </div>

          <div class="space-y-4 mt-6">
            <h4 class="text-lg font-semibold border-b border-gray-700 pb-2 flex justify-between items-center">
              Exclusions (Optional)
            </h4>
            <div class="space-y-3">
              <div v-for="(exc, index) in notificationForm.exclusions" :key="index" class="bg-gray-700 p-3 rounded-lg border border-gray-600 flex items-center gap-3">
                <select v-model="exc.type" class="bg-gray-800 border border-gray-600 rounded-lg px-2 py-1 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option value="time">Time Range</option>
                  <option value="weekday">Days of Week</option>
                </select>
                
                <div v-if="exc.type === 'time'" class="flex items-center gap-2 flex-grow">
                  <input v-model="exc.start" type="time" class="bg-gray-800 border border-gray-600 rounded-lg px-2 py-1 text-white text-sm w-full focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <span class="text-gray-400">to</span>
                  <input v-model="exc.end" type="time" class="bg-gray-800 border border-gray-600 rounded-lg px-2 py-1 text-white text-sm w-full focus:outline-none focus:ring-2 focus:ring-indigo-500">
                </div>
                
                <div v-else-if="exc.type === 'weekday'" class="flex items-center gap-1 flex-grow flex-wrap">
                  <label v-for="(day, dIndex) in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']" :key="dIndex" class="flex items-center gap-1 bg-gray-800 px-2 py-1 rounded text-xs cursor-pointer border border-gray-600 hover:border-indigo-500" :class="{'border-indigo-500 bg-indigo-900/30': exc.days?.includes(dIndex)}">
                    <input type="checkbox" :value="dIndex" v-model="exc.days" class="hidden">
                    {{ day }}
                  </label>
                </div>
                
                <button type="button" @click="notificationForm.exclusions.splice(index, 1)" class="text-red-400 hover:text-red-300 ml-auto">
                  &times;
                </button>
              </div>
            </div>
            <button type="button" @click="addExclusion" class="text-indigo-400 hover:text-indigo-300 text-sm font-medium transition-colors">+ Add Exclusion Rule</button>
          </div>
          
            </form>
          </div>
          <!-- Context Variables Column -->
          <div class="w-full md:w-80 bg-gray-900 rounded-xl border border-gray-700 flex flex-col overflow-hidden min-h-0">
            <div class="p-5 pb-0 shrink-0">
              <h4 class="text-lg font-bold text-white mb-2">Context Variables</h4>
              <p class="text-sm text-gray-400 mb-4">Use these variables in your notification title or payload. They will be dynamically replaced when the notification runs.</p>
            </div>
            <div class="p-5 pt-2 flex-1 overflow-y-auto custom-scrollbar min-h-0">
              <div v-if="contextVariables.length === 0" class="text-gray-500 text-sm italic">Loading variables...</div>
              <div v-else class="space-y-6">
                <div v-for="category in contextVariables" :key="category.category">
                  <h5 class="text-indigo-400 font-semibold mb-2 uppercase text-xs tracking-wider border-b border-gray-800 pb-1">{{ category.category }}</h5>
                  <ul class="space-y-3">
                    <li v-for="variable in category.variables" :key="variable.name" class="bg-gray-800 p-3 rounded border border-gray-700">
                      <div class="flex justify-between items-start mb-1">
                        <span class="font-mono text-sm text-pink-300 select-all cursor-pointer hover:text-pink-200 transition-colors break-all" @click="copyToClipboard(`{${variable.name}}`)">{{"{"}}{{ variable.name }}{{"}"}}</span>
                      </div>
                      <p class="text-xs text-gray-400 mb-1 leading-snug">{{ variable.description }}</p>
                      <p class="text-xs text-gray-500 font-mono italic break-words">Ex: {{ variable.example }}</p>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Footer Buttons -->
        <div class="mt-6 pt-5 border-t border-gray-700 flex justify-end gap-3 shrink-0">
          <button type="button" @click="showNotificationModal = false" class="px-5 py-2 text-gray-300 hover:text-white bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
          <button type="submit" form="notification-form" class="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors shadow-md">{{ isEditing ? 'Save Changes' : 'Create' }}</button>
        </div>
        
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
const contextVariables = ref([])

const showNotificationModal = ref(false)
const isEditing = ref(false)
const editingNotificationId = ref(null)
const notificationForm = ref({ channel_id: '', title: '', payload: '', schedule_type: 'specific_time', schedule_expr: '', parameters: {}, exclusions: [], start_time: '', is_active: true })
const specificTimeInputs = ref({ date: '', hour: '', minute: '' })
const intervalInputs = ref({ value: 10, unit: 'minutes' })
const cronInputs = ref({ min: '*', hour: '*', dom: '*', mon: '*', dow: '*' })
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



const logout = () => {
  authStore.logout()
  router.push('/login')
}

const getHeaders = () => ({ Authorization: `Bearer ${authStore.token}` })

const fetchDashboardData = async () => {
  try {
    const [channelsRes, notifsRes, pluginsRes, reposRes, contextRes] = await Promise.all([
      axios.get('http://localhost:8000/api/channels', { headers: getHeaders() }),
      axios.get('http://localhost:8000/api/notifications', { headers: getHeaders() }),
      axios.get('http://localhost:8000/api/channels/plugins', { headers: getHeaders() }),
      axios.get('http://localhost:8000/api/repositories', { headers: getHeaders() }),
      axios.get('http://localhost:8000/api/context', { headers: getHeaders() })
    ])
    
    channels.value = channelsRes.data
    notifications.value = notifsRes.data
    availablePlugins.value = pluginsRes.data
    contextVariables.value = contextRes.data
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

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text)
  showToast('Copied to clipboard!', 'success')
}

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

const handleSkipNext = async () => {
  try {
    await axios.post(`http://localhost:8000/api/notifications/${selectedNotification.value.id}/skip`, {}, { headers: getHeaders() })
    showSkipModal.value = false
    await fetchDashboardData()
    showToast(`Skipped next instance for: ${selectedNotification.value.title}`)
  } catch(e) {
    showToast('Failed to skip notification', 'error')
  }
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
  isEditing.value = false
  editingNotificationId.value = null
  notificationForm.value = { channel_id: '', title: '', payload: '', schedule_type: 'specific_time', schedule_expr: '', parameters: {}, exclusions: [], start_time: '', is_active: true }
  
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

const openEditNotification = (notif) => {
  isEditing.value = true
  editingNotificationId.value = notif.id
  
  notificationForm.value = { 
    channel_id: notif.channel_id, 
    title: notif.title, 
    payload: notif.payload || '', 
    schedule_type: notif.schedule_type, 
    schedule_expr: notif.schedule_expr, 
    parameters: { ...notif.parameters }, 
    exclusions: JSON.parse(JSON.stringify(notif.exclusions || [])).map(e => ({ ...e, tz_offset: e.tz_offset !== undefined ? e.tz_offset : new Date().getTimezoneOffset() })), 
    start_time: notif.start_time ? new Date(new Date(notif.start_time + 'Z').getTime() - (new Date().getTimezoneOffset() * 60000)).toISOString().slice(0, 16) : '',
    is_active: notif.is_active 
  }
  
  if (notif.schedule_type === 'specific_time') {
    try {
      const d = new Date(notif.schedule_expr)
      const offset = d.getTimezoneOffset() * 60000
      const localDate = new Date(d.getTime() - offset).toISOString().slice(0, 16)
      const [datePart, timePart] = localDate.split('T')
      const [hh, mm] = timePart.split(':')
      specificTimeInputs.value = { date: datePart, hour: hh, minute: mm }
    } catch(e) {
      console.error('Error parsing date:', e)
    }
  } else if (notif.schedule_type === 'interval') {
    const parts = notif.schedule_expr.split(' ')
    intervalInputs.value = { value: parseInt(parts[0]) || 10, unit: parts[1] || 'minutes' }
  } else if (notif.schedule_type === 'cron') {
    const parts = notif.schedule_expr.split(' ')
    cronInputs.value = { min: parts[0] || '*', hour: parts[1] || '*', dom: parts[2] || '*', mon: parts[3] || '*', dow: parts[4] || '*' }
  }
  
  showNotificationModal.value = true
}

const addExclusion = () => {
  notificationForm.value.exclusions.push({ type: 'time', start: '22:00', end: '08:00', days: [], tz_offset: new Date().getTimezoneOffset() })
}

const saveNotification = async () => {
  try {
    const payload = { ...notificationForm.value }
    if (payload.start_time) {
      payload.start_time = new Date(payload.start_time).toISOString()
    } else {
      payload.start_time = null
    }
    
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
    
    if (isEditing.value) {
      await axios.put(`http://localhost:8000/api/notifications/${editingNotificationId.value}`, payload, { headers: getHeaders() })
      showToast('Notification updated successfully')
    } else {
      await axios.post('http://localhost:8000/api/notifications', payload, { headers: getHeaders() })
      showToast('Notification created successfully')
    }
    showNotificationModal.value = false
    await fetchDashboardData()
  } catch(e) {
    showToast('Failed to save notification', 'error')
  }
}
</script>
