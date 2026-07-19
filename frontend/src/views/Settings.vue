<template>
  <div class="min-h-screen bg-gray-900 text-white pb-12 relative">
    <header class="bg-gray-800 shadow border-b border-gray-700">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
        <div class="flex items-center space-x-8">
          <div class="flex items-center space-x-3">
            <img src="/logo.png" alt="KeepMeUpdated Logo" class="w-10 h-10 object-contain drop-shadow-md" />
            <h1 class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">KeepMeUpdated</h1>
          </div>
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
          <button @click="showAddRepoModal = true" class="bg-indigo-600 hover:bg-indigo-500 text-white py-2 px-4 rounded-lg shadow-md transition-all">+ Add Repo</button>
        </div>
        <div v-if="repositories.length === 0" class="text-gray-400 text-center py-8 bg-gray-700/30 rounded-lg border border-dashed border-gray-600">No repositories added. Add one to download external plugins.</div>
        <ul class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <li v-for="repo in repositories" :key="repo.id" class="bg-gray-700 p-5 rounded-lg border border-gray-600 flex justify-between items-center">
            <div>
              <span class="font-semibold text-lg block">{{ repo.name }}</span>
              <span class="text-sm text-gray-400">{{ repo.url }}</span>
            </div>
            <div class="flex items-center space-x-3">
              <span v-if="repo.is_official" class="text-xs uppercase tracking-wider text-indigo-300 bg-indigo-900/50 px-2 py-1 rounded-full">Official</span>
              <button @click="viewRepoPlugins(repo)" class="text-indigo-400 hover:text-indigo-300 transition-colors text-sm font-medium">View Plugins</button>
              <button v-if="!repo.is_official" @click="confirmDeleteRepo(repo)" class="text-gray-400 hover:text-red-400 transition-colors text-sm">Delete</button>
            </div>
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
      
      <!-- Data Sources Section -->
      <section class="bg-gray-800 rounded-xl p-6 shadow-2xl border border-gray-700">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold">Data Sources</h2>
          <button @click="openAddDataSource" class="bg-indigo-600 hover:bg-indigo-500 text-white py-2 px-4 rounded-lg shadow-md transition-all transform hover:scale-105">+ Add Data Source</button>
        </div>
        <div v-if="dataSources.length === 0" class="text-gray-400 text-center py-8 bg-gray-700/30 rounded-lg border border-dashed border-gray-600">No data sources configured. Add one to inject dynamic context into notifications!</div>
        <ul class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <li v-for="ds in dataSources" :key="ds.id" class="flex flex-col bg-gray-700 p-5 rounded-lg border border-gray-600 hover:border-indigo-500 transition-colors group">
            <div class="flex justify-between items-start mb-2">
              <div>
                <span class="font-semibold text-lg">{{ ds.name }}</span>
                <span class="ml-2 text-xs uppercase tracking-wider text-pink-300 bg-pink-900/50 px-2 py-1 rounded-full">{{ ds.plugin_id }}</span>
              </div>
              <div class="flex items-center space-x-3">
                <span :class="ds.is_active ? 'text-green-400 bg-green-400/10' : 'text-red-400 bg-red-400/10'" class="px-2 py-1 rounded text-xs font-medium">
                  {{ ds.is_active ? 'Active' : 'Inactive' }}
                </span>
                <button @click="confirmDeleteDataSource(ds)" class="text-gray-400 hover:text-red-400 transition-colors text-sm">Delete</button>
                <button @click="openEditDataSource(ds)" class="text-gray-400 hover:text-white transition-colors">Edit</button>
                <SettingsIcon v-if="!ds.is_active" class="text-yellow-500 cursor-pointer hover:text-yellow-400 hover:rotate-90 transition-all w-5 h-5" @click="openEditDataSource(ds)" title="Configuration Required" />
              </div>
            </div>
          </li>
        </ul>
      </section>

      <!-- Custom Variables Section -->
      <section class="bg-gray-800 rounded-xl p-6 shadow-2xl border border-gray-700">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold">Custom Variables</h2>
          <button @click="openAddVariable" class="bg-indigo-600 hover:bg-indigo-500 text-white py-2 px-4 rounded-lg shadow-md transition-all transform hover:scale-105">+ Add Variable</button>
        </div>
        <div v-if="customVariables.length === 0" class="text-gray-400 text-center py-8 bg-gray-700/30 rounded-lg border border-dashed border-gray-600">No custom variables defined.</div>
        <ul class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <li v-for="cv in customVariables" :key="cv.id" class="flex flex-col bg-gray-700 p-5 rounded-lg border border-gray-600 hover:border-indigo-500 transition-colors group">
            <div class="flex justify-between items-start mb-2">
              <div>
                <span class="font-semibold text-lg text-indigo-300">{{"{"}}{{ cv.name }}{{"}"}}</span>
                <span class="block text-sm text-gray-300 mt-1 truncate" :title="cv.value">{{ cv.value }}</span>
              </div>
              <div class="flex items-center space-x-3 mt-1">
                <button @click="confirmDeleteVariable(cv)" class="text-gray-400 hover:text-red-400 transition-colors text-sm">Delete</button>
                <button @click="openEditVariable(cv)" class="text-gray-400 hover:text-white transition-colors text-sm">Edit</button>
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
              <option v-for="plugin in availableChannelPlugins" :key="plugin.id" :value="plugin.id">{{ plugin.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1">Channel Name</label>
            <input v-model="channelForm.name" type="text" required placeholder="e.g., Personal Email" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
          </div>
          
          <div v-if="selectedChannelSchema" class="space-y-4 mt-6">
            <h4 class="text-lg font-semibold border-b border-gray-700 pb-2">Configuration</h4>
            <div v-for="(field, key) in selectedChannelSchema.properties" :key="key">
              <label class="block text-sm font-medium text-gray-300 mb-1">{{ field.title || key }} <span v-if="selectedChannelSchema.required?.includes(key)" class="text-red-400">*</span></label>
              <select v-if="field.enum" v-model="channelForm.config[key]" :required="selectedChannelSchema.required?.includes(key)" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option v-for="option in field.enum" :key="option" :value="option">{{ option }}</option>
              </select>
              <div v-else-if="field.dynamic_options" class="flex items-center space-x-2">
                <select v-if="dynamicOptionsCache[channelForm.plugin_id + '_' + key]" v-model="channelForm.config[key]" :required="selectedChannelSchema.required?.includes(key)" class="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option v-for="opt in dynamicOptionsCache[channelForm.plugin_id + '_' + key]" :key="opt" :value="opt">{{ opt }}</option>
                </select>
                <input v-else v-model="channelForm.config[key]" type="text" :required="selectedChannelSchema.required?.includes(key)" class="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <button type="button" @click="fetchDynamicOptions(channelForm.plugin_id, key)" :disabled="isFetchingOptions[channelForm.plugin_id + '_' + key]" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg transition-colors shadow-md text-sm font-medium whitespace-nowrap flex items-center justify-center min-w-[80px]">
                  <span v-if="isFetchingOptions[channelForm.plugin_id + '_' + key]">Scanning...</span>
                  <span v-else>Scan</span>
                </button>
              </div>
              <input v-else-if="field.type === 'string' && field.format !== 'password'" v-model="channelForm.config[key]" type="text" :required="selectedChannelSchema.required?.includes(key)" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <input v-else-if="field.type === 'string' && field.format === 'password'" v-model="channelForm.config[key]" type="password" :required="selectedChannelSchema.required?.includes(key)" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <input v-else-if="field.type === 'integer'" v-model.number="channelForm.config[key]" type="number" :required="selectedChannelSchema.required?.includes(key)" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <div v-else-if="field.type === 'boolean'" class="flex items-center">
                <input v-model="channelForm.config[key]" type="checkbox" class="w-4 h-4 text-indigo-600 bg-gray-700 border-gray-600 rounded focus:ring-indigo-500 focus:ring-2">
                <span class="ml-2 text-sm text-gray-300">Enable</span>
              </div>
            </div>
          </div>
          
          <div class="flex justify-end gap-3 mt-8">
            <button v-if="channelForm.plugin_id" type="button" @click="testChannel" class="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors shadow-md mr-auto">Test Connection</button>
            <button type="button" @click="showChannelModal = false" class="px-5 py-2 text-gray-300 hover:text-white bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
            <button type="submit" class="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors shadow-md">Save</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Data Source Modal -->
    <div v-if="showDataSourceModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-gray-800 p-8 pt-6 pb-6 rounded-2xl w-full border border-gray-600 shadow-2xl flex flex-col max-h-[90vh] overflow-hidden transition-all duration-300" :class="testDataSourceResults ? 'max-w-4xl' : 'max-w-lg'">
        <h3 class="text-2xl font-bold mb-6 text-white shrink-0">{{ editingDataSource ? 'Edit Data Source' : 'Add Data Source' }}</h3>
        
        <div class="flex-1 flex flex-col md:flex-row gap-8 overflow-hidden min-h-0">
          <div class="flex-1 overflow-y-auto pr-4 custom-scrollbar">
            <form id="ds-form" @submit.prevent="saveDataSource" class="space-y-4 pb-4">
              <div v-if="!editingDataSource">
                <label class="block text-sm font-medium text-gray-300 mb-1">Plugin Type</label>
                <select v-model="dsForm.plugin_id" required class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option disabled value="">Select a plugin...</option>
                  <option v-for="plugin in availableDataSourcePlugins" :key="plugin.id" :value="plugin.id">{{ plugin.name }}</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-300 mb-1">Data Source Name</label>
                <input v-model="dsForm.name" type="text" required placeholder="e.g., My Local Weather" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              </div>
              
              <div v-if="selectedDataSourceSchema" class="space-y-4 mt-6">
                <h4 class="text-lg font-semibold border-b border-gray-700 pb-2">Configuration</h4>
                <div v-for="(field, key) in selectedDataSourceSchema.properties" :key="key">
                  <label class="block text-sm font-medium text-gray-300 mb-1">{{ field.title || key }} <span v-if="selectedDataSourceSchema.required?.includes(key)" class="text-red-400">*</span></label>
                  <select v-if="field.enum" v-model="dsForm.config[key]" :required="selectedDataSourceSchema.required?.includes(key)" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option v-for="option in field.enum" :key="option" :value="option">{{ option }}</option>
                  </select>
                  <input v-else-if="field.type === 'string' && field.format !== 'password'" v-model="dsForm.config[key]" type="text" :required="selectedDataSourceSchema.required?.includes(key)" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <input v-else-if="field.type === 'string' && field.format === 'password'" v-model="dsForm.config[key]" type="password" :required="selectedDataSourceSchema.required?.includes(key)" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <input v-else-if="field.type === 'integer'" v-model.number="dsForm.config[key]" type="number" :required="selectedDataSourceSchema.required?.includes(key)" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <div v-else-if="field.type === 'boolean'" class="flex items-center">
                    <input v-model="dsForm.config[key]" type="checkbox" class="w-4 h-4 text-indigo-600 bg-gray-700 border-gray-600 rounded focus:ring-indigo-500 focus:ring-2">
                    <span class="ml-2 text-sm text-gray-300">Enable</span>
                  </div>
                </div>
              </div>
            </form>
          </div>

          <!-- Test Results Side Panel -->
          <div v-if="testDataSourceResults" class="w-full md:w-80 bg-gray-900 rounded-xl border border-gray-700 flex flex-col overflow-hidden min-h-0">
            <div class="p-5 pb-0 shrink-0">
              <h4 class="text-lg font-bold text-white mb-2">Test Results</h4>
              <p class="text-sm text-gray-400 mb-4">Variables populated by the current connection.</p>
            </div>
            <div class="p-5 pt-2 flex-1 overflow-y-auto custom-scrollbar min-h-0">
              <ul class="space-y-3">
                <li v-for="(value, key) in testDataSourceResults" :key="key" class="bg-gray-800 p-3 rounded border border-gray-700">
                  <span class="font-mono text-sm text-pink-300 block mb-1 select-all break-all">{{"{"}}{{ key }}{{"}"}}</span>
                  <span class="text-gray-300 text-sm break-words">{{ value }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div class="mt-6 pt-5 border-t border-gray-700 flex justify-end gap-3 shrink-0">
          <button v-if="dsForm.plugin_id" type="button" @click="testDataSource" class="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors shadow-md mr-auto disabled:opacity-50" :disabled="isTestingDataSource">
            <span v-if="isTestingDataSource">Testing...</span>
            <span v-else>Test Connection</span>
          </button>
          <button type="button" @click="closeDataSourceModal" class="px-5 py-2 text-gray-300 hover:text-white bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
          <button type="submit" form="ds-form" class="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors shadow-md">Save</button>
        </div>
      </div>
    </div>

    <!-- Custom Variable Modal -->
    <div v-if="showVariableModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-gray-800 p-8 rounded-2xl max-w-lg w-full border border-gray-600 shadow-2xl">
        <h3 class="text-2xl font-bold mb-6 text-white">{{ editingVariable ? 'Edit Custom Variable' : 'Add Custom Variable' }}</h3>
        <form @submit.prevent="saveVariable" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1">Variable Name</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400">{{"{"}}</span>
              <input v-model="cvForm.name" type="text" required placeholder="e.g. companyName" class="w-full bg-gray-700 border border-gray-600 rounded-lg pl-6 pr-6 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <span class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400">{{"}"}}</span>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1">Value</label>
            <input v-model="cvForm.value" type="text" required placeholder="e.g. Acme Corp" class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
          </div>
          <div class="flex justify-end gap-3 mt-8">
            <button type="button" @click="showVariableModal = false" class="px-5 py-2 text-gray-300 hover:text-white bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
            <button type="submit" class="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors shadow-md">Save</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add Repo Modal -->
    <div v-if="showAddRepoModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-gray-800 p-8 rounded-2xl max-w-lg w-full border border-gray-600 shadow-2xl">
        <h3 class="text-2xl font-bold mb-6 text-white">Add Repository</h3>
        <div class="bg-yellow-900/50 border border-yellow-700 p-4 rounded-lg mb-6 flex items-start space-x-3">
          <svg class="w-6 h-6 text-yellow-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          <p class="text-yellow-400 text-sm leading-relaxed">
            <strong class="font-bold">Security Warning:</strong> Only add repositories from trusted sources. Installing plugins may execute arbitrary code and dynamically install python dependencies on your server.
          </p>
        </div>
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
    
    <!-- Repo Plugins Modal -->
    <div v-if="showRepoPluginsModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-gray-800 p-8 rounded-2xl max-w-2xl w-full border border-gray-600 shadow-2xl">
        <h3 class="text-2xl font-bold mb-6 text-white">{{ selectedRepo?.name }} - Plugins</h3>
        <div v-if="loadingPlugins" class="text-center py-8 text-gray-400">Loading plugins...</div>
        <div v-else-if="repoPlugins.length === 0" class="text-gray-400 text-center py-8 bg-gray-700/30 rounded-lg border border-dashed border-gray-600">No plugins found in this repository.</div>
        <ul v-else class="space-y-4 max-h-[60vh] overflow-y-auto pr-2 custom-scrollbar">
          <li v-for="plugin in repoPlugins" :key="plugin.id" class="bg-gray-700 p-4 rounded-lg border border-gray-600 flex justify-between items-center">
            <div>
              <span class="font-semibold text-lg block">{{ plugin.name }} <span class="text-xs text-gray-400 ml-2">v{{ plugin.version }}</span></span>
              <span class="text-sm text-gray-300 block mt-1">{{ plugin.description }}</span>
              <span v-if="plugin.requirements && plugin.requirements.length > 0" class="text-xs text-indigo-300 block mt-2 font-medium">Requires: {{ plugin.requirements.join(', ') }}</span>
            </div>
            <div class="ml-4 flex-shrink-0 flex items-center space-x-2">
              <template v-if="plugin.is_installed">
                <span v-if="plugin.installed_version === plugin.version" class="text-xs uppercase tracking-wider text-green-400 bg-green-900/50 px-3 py-2 rounded-lg font-semibold border border-green-700">Installed</span>
                <button v-else @click="installPlugin(plugin)" class="bg-yellow-600 hover:bg-yellow-500 text-white py-2 px-4 rounded-lg shadow-md transition-all font-medium text-sm">Update</button>
                <button @click="uninstallPlugin(plugin)" class="bg-red-600 hover:bg-red-500 text-white py-2 px-4 rounded-lg shadow-md transition-all font-medium text-sm">Uninstall</button>
              </template>
              <button v-else @click="installPlugin(plugin)" class="bg-indigo-600 hover:bg-indigo-500 text-white py-2 px-4 rounded-lg shadow-md transition-all font-medium text-sm">Install</button>
            </div>
          </li>
        </ul>
        <div class="flex justify-end mt-8">
          <button @click="showRepoPluginsModal = false" class="px-5 py-2 text-gray-300 hover:text-white bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Close</button>
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
import { Settings as SettingsIcon } from 'lucide-vue-next'

const authStore = useAuthStore()
const router = useRouter()

const channels = ref([])
const dataSources = ref([])
const customVariables = ref([])
const availablePlugins = ref([])
const repositories = ref([])

// Modals State
const showChannelModal = ref(false)
const editingChannel = ref(null)
const channelForm = ref({ plugin_id: '', name: '', config: {}, is_active: true })

const dynamicOptionsCache = ref({})
const isFetchingOptions = ref({})

const fetchDynamicOptions = async (pluginId, fieldName) => {
  const cacheKey = `${pluginId}_${fieldName}`
  isFetchingOptions.value[cacheKey] = true
  try {
    const res = await axios.get(`/api/channels/options/${pluginId}/${fieldName}`, { headers: getHeaders() })
    dynamicOptionsCache.value[cacheKey] = res.data
    showToast('Scan complete')
  } catch (e) {
    showToast('Failed to fetch options', 'error')
  } finally {
    isFetchingOptions.value[cacheKey] = false
  }
}

const showDataSourceModal = ref(false)
const editingDataSource = ref(null)
const dsForm = ref({ plugin_id: '', name: '', config: {}, is_active: true })
const testDataSourceResults = ref(null)
const isTestingDataSource = ref(false)

const showVariableModal = ref(false)
const editingVariable = ref(null)
const cvForm = ref({ name: '', value: '' })

const showAddRepoModal = ref(false)
const repoForm = ref({ name: '', url: '' })

const showConfirmModal = ref(false)
const confirmModalState = ref({ title: '', message: '', onConfirm: null })

const showRepoPluginsModal = ref(false)
const selectedRepo = ref(null)
const repoPlugins = ref([])
const loadingPlugins = ref(false)

// Toast State
const toast = ref({ show: false, message: '', type: 'success' })
const showToast = (message, type = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => toast.value.show = false, 3000)
}

const availableChannelPlugins = computed(() => availablePlugins.value.filter(p => p.type === 'channel'))
const availableDataSourcePlugins = computed(() => availablePlugins.value.filter(p => p.type === 'datasource'))

const selectedChannelSchema = computed(() => {
  const plugin = availablePlugins.value.find(p => p.id === channelForm.value.plugin_id)
  return plugin ? plugin.schema : null
})

const selectedDataSourceSchema = computed(() => {
  const plugin = availablePlugins.value.find(p => p.id === dsForm.value.plugin_id)
  return plugin ? plugin.schema : null
})

watch(() => channelForm.value.plugin_id, (newPluginId) => {
  if (!editingChannel.value && newPluginId) {
    channelForm.value.config = {}
  }
})

watch(() => dsForm.value.plugin_id, (newPluginId) => {
  if (!editingDataSource.value && newPluginId) {
    dsForm.value.config = {}
  }
})

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const getHeaders = () => ({ Authorization: `Bearer ${authStore.token}` })

const fetchSettingsData = async () => {
  try {
    const [channelsRes, dsRes, cvRes, pluginsRes, reposRes] = await Promise.all([
      axios.get('/api/channels/', { headers: getHeaders() }),
      axios.get('/api/data-sources/', { headers: getHeaders() }),
      axios.get('/api/custom-variables/', { headers: getHeaders() }),
      axios.get('/api/channels/plugins', { headers: getHeaders() }), // This endpoint returns ALL plugins now
      axios.get('/api/repositories/', { headers: getHeaders() })
    ])
    
    channels.value = channelsRes.data
    dataSources.value = dsRes.data
    customVariables.value = cvRes.data
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
    await axios.post('/api/repositories/', repoForm.value, { headers: getHeaders() })
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
        await axios.delete(`/api/repositories/${repo.id}`, { headers: getHeaders() })
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

const viewRepoPlugins = async (repo) => {
  selectedRepo.value = repo
  showRepoPluginsModal.value = true
  loadingPlugins.value = true
  repoPlugins.value = []
  try {
    const res = await axios.get(`/api/repositories/${repo.id}/plugins`, { headers: getHeaders() })
    repoPlugins.value = res.data
  } catch(e) {
    showToast('Failed to load plugins', 'error')
  } finally {
    loadingPlugins.value = false
  }
}

const installPlugin = async (plugin) => {
  try {
    const payload = { 
      plugin_id: plugin.id, 
      version: plugin.version, 
      full_file_url: plugin.full_file_url 
    };
    if (plugin.requirements) {
      payload.requirements = plugin.requirements;
    }
    await axios.post('/api/repositories/install', payload, { headers: getHeaders() })
    plugin.is_installed = true
    plugin.installed_version = plugin.version
    await fetchSettingsData()
    showToast(`${plugin.name} installed successfully`)
  } catch(e) {
    showToast(`Failed to install ${plugin.name}`, 'error')
  }
}

const uninstallPlugin = async (plugin) => {
  try {
    await axios.post('/api/repositories/uninstall', { plugin_id: plugin.id }, { headers: getHeaders() })
    plugin.is_installed = false
    plugin.installed_version = null
    await fetchSettingsData()
    showToast(`${plugin.name} uninstalled successfully`)
  } catch(e) {
    showToast(`Failed to uninstall ${plugin.name}`, 'error')
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
        await axios.delete(`/api/channels/${channel.id}`, { headers: getHeaders() })
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
      await axios.put(`/api/channels/${editingChannel.value.id}`, channelForm.value, { headers: getHeaders() })
    } else {
      await axios.post('/api/channels/', channelForm.value, { headers: getHeaders() })
    }
    showChannelModal.value = false
    await fetchSettingsData()
    showToast('Channel saved successfully')
  } catch(e) {
    showToast('Failed to save channel', 'error')
  }
}

const testChannel = async () => {
  if (!channelForm.value.plugin_id) return
  try {
    await axios.post('/api/channels/test', channelForm.value, { headers: getHeaders() })
    showToast('Test notification sent successfully!', 'success')
  } catch(e) {
    showToast(e.response?.data?.detail || 'Test notification failed', 'error')
  }
}

// Data Sources logic
const openAddDataSource = () => {
  editingDataSource.value = null
  dsForm.value = { plugin_id: '', name: '', config: {}, is_active: true }
  testDataSourceResults.value = null
  showDataSourceModal.value = true
}

const openEditDataSource = (ds) => {
  editingDataSource.value = ds
  dsForm.value = { ...ds, config: { ...ds.config } }
  testDataSourceResults.value = null
  showDataSourceModal.value = true
}

const closeDataSourceModal = () => {
  showDataSourceModal.value = false
  testDataSourceResults.value = null
}

const confirmDeleteDataSource = (ds) => {
  confirmModalState.value = {
    title: 'Delete Data Source',
    message: `Are you sure you want to delete ${ds.name}? Notifications relying on its context variables will no longer be able to resolve them.`,
    onConfirm: async () => {
      try {
        await axios.delete(`/api/data-sources/${ds.id}`, { headers: getHeaders() })
        showConfirmModal.value = false
        await fetchSettingsData()
        showToast('Data source deleted')
      } catch(e) {
        showToast('Failed to delete data source', 'error')
      }
    }
  }
  showConfirmModal.value = true
}

const saveDataSource = async () => {
  try {
    dsForm.value.is_active = true; 
    if (editingDataSource.value) {
      await axios.put(`/api/data-sources/${editingDataSource.value.id}`, dsForm.value, { headers: getHeaders() })
    } else {
      await axios.post('/api/data-sources/', dsForm.value, { headers: getHeaders() })
    }
    showDataSourceModal.value = false
    await fetchSettingsData()
    showToast('Data source saved successfully')
  } catch(e) {
    showToast('Failed to save data source', 'error')
  }
}

const testDataSource = async () => {
  if (!dsForm.value.plugin_id) return
  isTestingDataSource.value = true
  testDataSourceResults.value = null
  try {
    const res = await axios.post('/api/data-sources/test', dsForm.value, { headers: getHeaders() })
    testDataSourceResults.value = res.data.context
    showToast('Test connection successful!', 'success')
  } catch(e) {
    showToast(e.response?.data?.detail || 'Test connection failed', 'error')
  } finally {
    isTestingDataSource.value = false
  }
}

// Custom Variables Logic
const openAddVariable = () => {
  editingVariable.value = null
  cvForm.value = { name: '', value: '' }
  showVariableModal.value = true
}

const openEditVariable = (cv) => {
  editingVariable.value = cv
  cvForm.value = { ...cv }
  showVariableModal.value = true
}

const confirmDeleteVariable = (cv) => {
  confirmModalState.value = {
    title: 'Delete Custom Variable',
    message: `Are you sure you want to delete '{${cv.name}}'? Notifications using it will no longer resolve it.`,
    onConfirm: async () => {
      try {
        await axios.delete(`/api/custom-variables/${cv.id}`, { headers: getHeaders() })
        showConfirmModal.value = false
        await fetchSettingsData()
        showToast('Variable deleted')
      } catch(e) {
        showToast('Failed to delete variable', 'error')
      }
    }
  }
  showConfirmModal.value = true
}

const saveVariable = async () => {
  try {
    // Basic sanitization
    cvForm.value.name = cvForm.value.name.replace(/[^a-zA-Z0-9_]/g, '')
    if (editingVariable.value) {
      await axios.put(`/api/custom-variables/${editingVariable.value.id}`, cvForm.value, { headers: getHeaders() })
    } else {
      await axios.post('/api/custom-variables/', cvForm.value, { headers: getHeaders() })
    }
    showVariableModal.value = false
    await fetchSettingsData()
    showToast('Variable saved successfully')
  } catch(e) {
    showToast(e.response?.data?.detail || 'Failed to save variable', 'error')
  }
}
</script>
