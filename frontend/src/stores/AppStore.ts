import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { ServerRealmOption } from '../services/models';

export const useAppStore = defineStore('app', () => {
    // States
    const selectedServerRealmOption = ref<ServerRealmOption | null>(null);
    const searchQuery = ref<string>('');

    // Getters
    const getSelectedServerRealm = () => selectedServerRealmOption.value;
    const getSelectedServer = () => selectedServerRealmOption.value?.server || null;
    const getSelectedServerSlug = () => selectedServerRealmOption.value?.server_slug || null;
    const getSelectedRealm = () => selectedServerRealmOption.value?.realm || null;
    const getSelectedRealmSlug = () => selectedServerRealmOption.value?.realm_slug || null;
    const getSearchQuery = () => searchQuery.value;

    // Actions
    const setSelectedServerRealmOption = (serverRealm: ServerRealmOption | null) => {
        selectedServerRealmOption.value = serverRealm;
    };
    const clearSelectedServerRealmOption = () => {
        selectedServerRealmOption.value = null;
    };
    const setSearchQuery = (query: string) => {
        searchQuery.value = query;
    };
    const clearSearchQuery = () => {
        searchQuery.value = '';
    };

    return {
        // State
        selectedServerRealmOption,
        searchQuery,

        // Getters
        getSelectedServerRealm,
        getSelectedServer,
        getSelectedServerSlug,
        getSelectedRealm,
        getSelectedRealmSlug,
        getSearchQuery,

        // Actions
        setSelectedServerRealmOption,
        clearSelectedServerRealmOption,
        setSearchQuery,
        clearSearchQuery
    };
});
