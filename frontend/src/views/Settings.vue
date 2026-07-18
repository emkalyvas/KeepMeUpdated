<template>
  <div class="min-h-screen bg-gray-900 text-white pb-12 relative">
    <header class="bg-gray-800 shadow border-b border-gray-700">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
        <div class="flex items-center space-x-8">
          <h1 class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">KeepMeUpdated</h1>
          <nav class="hidden md:flex space-x-4">
            <router-link to="/" class="text-gray-400 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">Dashboard</router-link>
            <router-link to="/settings" class="text-white bg-gray-900 px-3 py-2 rounded-md text-sm font-medium">Settings</router-link>
          </nav>
        </div>
        <button @click="logout" class="text-gray-300 hover:text-white transition-colors">Logout</button>
      </div>
    </header>
    
    <main class="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8 space-y-8">
      
      <!-- Repositories Section -->
      <section class="bg-gray-800 rounded-xl p-6 shadow-2xl border border-gray-700">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold">Plugin Repositories</h2>
          <div class="flex space-x-2">
            <button @click="syncRepositories" class="bg-gray-600 hover:bg-gray-500 text-white py-2 px-4 rounded-lg shadow-md transition-all">Sync Plugins</button>
            <button @click="showAddRepoModal = true" class="bg-indigo-600 hover:bg-indigo-500 text-white py-2 px-4 rounded-lg shadow-md transition-all">+ Add Repo</button>
          </div>
        </div>
        <div v-if="repositories.length === 0" class="text-gray-400 text-center py-8 bg-gray-700/30 rounded-lg border border-dashed border-gray-600">No repositories added. Add one to download external plugins.</div>
        <ul class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <li v-for="repo in repositories" :key="repo.id" class="bg-gray-700 p-5 rounded-lg border border-gray-600 flex justify-between items-center">
            <div>
              <span class="font-semibold text-lg block">{{ repo.name }}</span>
              <span class="text-sm text-gray-400">{{ repo.url }}</span>
            </div>
            <button @click="confirmDeleteRepo(repo)" class="text-gray-400 hover:text-red-400 transition-colors text-sm">Delete</button>
          </li>
        </ul>
      </section>

      <!-- Channels Section -->
      <section class="bg-gray-800 rounded-xl p-6 shadow-2xl border border-gray-700">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold">My Channels</h2>
          <button @click="openAddChannel" class="bg-indigo-600 hover:bg-indigo-500 text-white py-2 px-4 rounded-lg shadow-md transition-all transform hover:scale-105">+ Add Channel</button>
        </div>
        <div v-if="channels.length === 0" class="text-gray-400 text-center py-8 bg-gray-700/30 rounded-lg border border-dashed border-gray-600">No channels configured. Add one to get started!</div>
        <ul class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <li v-for="channel in channels" :key="channel.id" class="flex flex-col bg-gray-700 p-5 rounded-lg border border-gray-600 hover:border-indigo-500 transition-colors group">
            <div class="flex justify-between items-start mb-2">
              <div>
                <span class="font-semibold text-lg">{{ channel.name }}</span>
                <span class="ml-2 text-xs uppercase tracking-wider text-indigo-300 bg-indigo-900/50 px-2 py-1 rounded-full">{{ channel.plugin_id }}</span>
              </div>
              <div class="flex items-center space-x-3">
                <span :class="channel.is_active ? 'text-green-400 bg-green-400/10' : 'text-red-400 bg-red-400/10'" class="px-2 py-1 rounded text-xs font-medium">
                  {{ channel.is_active ? 'Active' : 'Inactive' }}
                </span>
                <button @click="confirmDeleteChannel(channel)" class="text-gray-400 hover:text-red-400 transition-colors text-sm">Delete</button>
                <button @click="openEditChannel(channel)" class="text-gray-400 hover:text-white transition-colors">Edit</button>
                <SettingsIcon v-if="!channel.is_active" class="text-yellow-500 cursor-pointer hover:text-yellow-400 hover:rotate-90 transition-all w-5 h-5" @click="openEditChannel(channel)" title="Configuration Required" />
              </div>
            </div>
          </li>
        </ul>
      </section>
    </main>

    <!-- Channel Modal -->
    <div v-if="showChannelModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-gray-800 p-8 rounded-2xl max-w-lg w-full border border-gray-600 shadow-2xl overflow-y-auto max-h-[90vh]">
        <h3 class="text-2xl font-bold mb-6 text-white">{{ editingChannel ? 'Edit Channel' : 'Add Channel' }}</h3>
        <form @submit.prevent="saveChannel" class="space-y-4">
          <div v-if="!editingChannel">
            <label class="block text-sm font-medium text-gray-300 mb-1">Plugin Type</label>
            <select v-model="channelForm.plugin_id" required class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option disabled value="">Select a plugin...</option>
              <option v-for="plugin in availablePlugins" :key="plugin.id" :value="plugin.id">{{ plugin.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1">Channel Name</label>
            <input v-model="channelForm.name" type="text" required placeholder="e.g., Personal Email" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
          </div>
          
          <div v-if="selectedPluginSchema" class="space-y-4 mt-6">
            <h4 class="text-lg font-semibold border-b border-gray-700 pb-2">Configuration</h4>
            <div v-for="(field, key) in selectedPluginSchema.properties" :key="key">
              <label class="block text-sm font-medium text-gray-300 mb-1">{{ field.title || key }} <span v-if="selectedPluginSchema.required?.includes(key)" class="text-red-400">*</span></label>
              <input v-if="field.type === 'string' && field.format !== 'password'" v-model="channelForm.config[key]" type="text" :required="selectedPluginSchema.required?.includes(key)" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <input v-else-if="field.type === 'string' && field.format === 'password'" v-model="channelForm.config[key]" type="password" :required="selectedPluginSchema.required?.includes(key)" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <input v-else-if="field.type === 'integer'" v-model.number="channelForm.config[key]" type="number" :required="selectedPluginSchema.required?.includes(key)" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <div v-else-if="field.type === 'boolean'" class="flex items-center">
                <input v-model="channelForm.config[key]" type="checkbox" class="w-4 h-4 text-indigo-600 bg-gray-700 border-gray-600 rounded focus:ring-indigo-500 focus:ring-2">
                <span class="ml-2 text-sm text-gray-300">Enable</span>
              </div>
            </div>
          </div>
          
          <div class="flex justify-end gap-3 mt-8">
            <button type="button" @click="showChannelModal = false" class="px-5 py-2 text-gray-300 hover:text-white bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
            <button type="submit" class="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors shadow-md">Save</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add Repo Modal -->
    <div v-if="showAddRepoModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-gray-800 p-8 rounded-2xl max-w-lg w-full border border-gray-600 shadow-2xl">
        <h3 class="text-2xl font-bold mb-6 text-white">Add Repository</h3>
        <form @submit.prevent="addRepository" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1">Repository Name</label>
            <input v-model="repoForm.name" type="text" required placeholder="e.g. Official Plugins" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1">URL (to registry.json)</label>
            <input v-model="repoForm.url" type="url" required placeholder="http://..." class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
          </div>
          <div class="flex justify-end gap-3 mt-8">
            <button type="button" @click="showAddRepoModal = false" class="px-5 py-2 text-gray-300 hover:text-white bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
            <button type="submit" class="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors shadow-md">Add</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirm Modal -->
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

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Settings as SettingsIcon } from 'lucide-vue-next'

const authStore = useAuthStore()
const router = useRouter()

const channels = ref([])
const availablePlugins = ref([])
const repositories = ref([])

// Modals State
const showChannelModal = ref(false)
const editingChannel = ref(null)
const channelForm = ref({ plugin_id: '', name: '', config: {}, is_active: true })

const showAddRepoModal = ref(false)
const repoForm = ref({ name: '', url: '' })

const showConfirmModal = ref(false)
const confirmModalState = ref({ title: '', message: '', onConfirm: null })

// Toast State
const toast = ref({ show: false, message: '', type: 'success' })
const showToast = (message, type = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => toast.value.show = false, 3000)
}

const selectedPluginSchema = computed(() => {
  const plugin = availablePlugins.value.find(p => p.id === channelForm.value.plugin_id)
  return plugin ? plugin.schema : null
})

watch(() => channelForm.value.plugin_id, (newPluginId) => {
  if (!editingChannel.value && newPluginId) {
    channelForm.value.config = {}
  }
})

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const getHeaders = () => ({ Authorization: `Bearer ${authStore.token}` })

const fetchSettingsData = async () => {
  try {
    const [channelsRes, pluginsRes, reposRes] = await Promise.all([
      axios.get('http://localhost:8000/api/channels', { headers: getHeaders() }),
      axios.get('http://localhost:8000/api/channels/plugins', { headers: getHeaders() }),
      axios.get('http://localhost:8000/api/repositories', { headers: getHeaders() })
    ])
    
    channels.value = channelsRes.data
    availablePlugins.value = pluginsRes.data
    repositories.value = reposRes.data
  } catch (error) {
    if (error.response?.status === 401) {
      logout()
    } else {
      showToast('Failed to load settings', 'error')
    }
  }
}

onMounted(() => {
  fetchSettingsData()
})

// Repositories logic
const addRepository = async () => {
  try {
    await axios.post('http://localhost:8000/api/repositories', repoForm.value, { headers: getHeaders() })
    showAddRepoModal.value = false
    repoForm.value = { name: '', url: '' }
    await fetchSettingsData()
    showToast('Repository added successfully')
  } catch(e) {
    showToast('Failed to add repository', 'error')
  }
}

const confirmDeleteRepo = (repo) => {
  confirmModalState.value = {
    title: 'Delete Repository',
    message: `Are you sure you want to delete ${repo.name}? This will not remove installed plugins, but will prevent future updates.`,
    onConfirm: async () => {
      try {
        await axios.delete(`http://localhost:8000/api/repositories/${repo.id}`, { headers: getHeaders() })
        showConfirmModal.value = false
        await fetchSettingsData()
        showToast('Repository deleted')
      } catch(e) {
        showToast('Failed to delete repository', 'error')
      }
    }
  }
  showConfirmModal.value = true
}

const syncRepositories = async () => {
  try {
    await axios.post('http://localhost:8000/api/repositories/sync', {}, { headers: getHeaders() })
    await fetchSettingsData()
    showToast('Plugins synced successfully')
  } catch(e) {
    showToast('Failed to sync plugins', 'error')
  }
}

// Channels logic
const openAddChannel = () => {
  editingChannel.value = null
  channelForm.value = { plugin_id: '', name: '', config: {}, is_active: true }
  showChannelModal.value = true
}

const openEditChannel = (channel) => {
  editingChannel.value = channel
  channelForm.value = { ...channel, config: { ...channel.config } }
  showChannelModal.value = true
}

const confirmDeleteChannel = (channel) => {
  confirmModalState.value = {
    title: 'Delete Channel',
    message: `Are you sure you want to delete ${channel.name}? All associated notifications will also be deleted.`,
    onConfirm: async () => {
      try {
        await axios.delete(`http://localhost:8000/api/channels/${channel.id}`, { headers: getHeaders() })
        showConfirmModal.value = false
        await fetchSettingsData()
        showToast('Channel deleted')
      } catch(e) {
        showToast('Failed to delete channel', 'error')
      }
    }
  }
  showConfirmModal.value = true
}

const saveChannel = async () => {
  try {
    channelForm.value.is_active = true; 
    if (editingChannel.value) {
      await axios.put(`http://localhost:8000/api/channels/${editingChannel.value.id}`, channelForm.value, { headers: getHeaders() })
    } else {
      await axios.post('http://localhost:8000/api/channels', channelForm.value, { headers: getHeaders() })
    }
    showChannelModal.value = false
    await fetchSettingsData()
    showToast('Channel saved successfully')
  } catch(e) {
    showToast('Failed to save channel', 'error')
  }
}
</script>
