<!-- Search Page, contains results from the search query params -->
<!-- We search on items and within items we show a list of auctions for it -->

<template>
    <main class="container">
        <DynamicContent>
            <div class="header-row">
                <hgroup>
                    <p class="chapter"
                        ><router-link :to="`/ah/${serverSlug}/${realmSlug}`">{{ server_name }} • {{ realm_name }}</router-link></p
                    >
                    <h1
                        >Results for <i>{{ item_name || 'All items' }}</i></h1
                    >
                    <p :aria-busy="loading"
                        ><span v-if="loading"></span
                        ><span v-else
                            >Displaying {{ results.data?.length || 0 }} item(s) out of {{ results.pagination?.total || 0 }} found</span
                        ></p
                    >
                </hgroup>
            </div>

            <hr />

            <DataGrid :data="results.data || []" :columns="columns" :loading="loading" :onItemClick="handleItemClick" @sort="handleSort">
                <template #cell-name="{ item }">
                    <span class="name-container">
                        <WowIcon :icon="item.icon" :size="32" /><span :class="getQualityColor(item.quality)">{{ item.name }}</span></span
                    >
                </template>
                <template #cell-vendor_price="{ value }">
                    <span v-if="value" v-html="getFormattedPriceHtml(value)"></span>
                    <span v-else>N/A</span>
                </template>
            </DataGrid>
        </DynamicContent>
    </main>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Item } from '../services/models';
import { API } from '../services/api-service';
import DataGrid, { type GridColumn } from '../components/DataGrid.vue';
import { getFormattedPriceHtml, getQualityColor, toSlug } from '../common/util';
import DynamicContent from '../components/DynamicContent.vue';
import WowIcon from '../components/WowIcon.vue';
import { useAppStore } from '../stores/AppStore';
import { useSeoMeta } from '@unhead/vue';

const route = useRoute();
const router = useRouter();
const appStore = useAppStore();

// Get server/realm from route or store
const serverSlug = computed(() => (route.params.serverSlug as string) || appStore.getSelectedServerSlug());
const realmSlug = computed(() => (route.params.realmSlug as string) || appStore.getSelectedRealmSlug());

const server_name = ref<string>('');
const realm_name = ref<string>('');

// TODO: At some point we will want a list of filters
const item_name = ref<string>('');
const results = ref<{ data: Item[] }>({ data: [] }); // Initialize with empty array
const loading = ref<boolean>(false);

// Define grid columns
const columns: GridColumn[] = [
    { key: 'name', label: 'Item Name', sortable: true },
    { key: 'level', label: 'Level', sortable: true },
    { key: 'class_name', label: 'Category', sortable: true }
];

// Handle sorting
const handleSort = (key: string, order: 'asc' | 'desc') => {};

// Handle item click
const handleItemClick = (item: Item) => {
    const item_slug = toSlug(item.name);
    const back = window.location.pathname + window.location.search;

    router.push(`/ah/${serverSlug.value}/${realmSlug.value}/item/${item.id}/${item_slug}?back=${back}`);
};

// Load data function
const loadData = async () => {
    loading.value = true;

    try {
        // Get search query from route
        const item_name_param = route.query.item_name;
        if (item_name_param) {
            item_name.value = item_name_param as string;
        } else {
            item_name.value = '';
        }

        // Create the item filter
        const item_filter = {
            name: item_name.value
        };

        // Get the items
        const items = await API.items.getFiltered(serverSlug.value, realmSlug.value, item_filter);
        // Do some additional processing e.g. capitalize the class name
        items.data.forEach((item) => {
            item.class_name = item.class_name.charAt(0).toUpperCase() + item.class_name.slice(1);
        });
        results.value = items;
    } catch (error) {
        console.error('Error fetching items:', error);
        // Ensure we have a valid structure even on error
        results.value = { data: [] };
    } finally {
        loading.value = false;
    }
};

// Watch for route changes to reload data
watch(
    () => [route.query.item_name, route.params.serverSlug, route.params.realmSlug],
    () => {
        loadData();
    },
    { immediate: false }
);

onMounted(async () => {
    // Construct server and realm name from serverSlug and realmSlug and capitalize the first letter of each word
    server_name.value = serverSlug.value
        .split('-')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    realm_name.value = realmSlug.value
        .split('-')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

    await loadData();
});

// ----- SEO Meta -----
const seoServer = computed(() => server_name.value || 'WoW');
const seoRealm = computed(() => realm_name.value || 'Realm');
const seoSearchTerm = computed(() => item_name.value || 'items');
const seoTitle = computed(() => {
    return `Search "${seoSearchTerm.value}" - ${seoServer.value} • ${seoRealm.value} - Lotkeeper`;
});
const seoDescription = computed(() => {
    const searchTerm = seoSearchTerm.value;
    const server = seoServer.value;
    const realm = seoRealm.value;
    const resultCount = results.value.data?.length || 0;
    return `Search results for "${searchTerm}" on ${server} • ${realm}.\n\nFind ${resultCount} items with auction house data and pricing information.`;
});
const seoUrl = computed(() => {
    const searchParams = new URLSearchParams();
    if (item_name.value) searchParams.set('item_name', item_name.value);
    return `https://lotkeeper.net/ah/${serverSlug.value}/${realmSlug.value}/search?${searchParams.toString()}`;
});

useSeoMeta({
    title: seoTitle,
    description: seoDescription,
    ogTitle: seoTitle,
    ogDescription: seoDescription,
    twitterTitle: seoTitle,
    twitterDescription: seoDescription,
    ogUrl: seoUrl,
    twitterUrl: seoUrl
});
</script>

<style scoped>
.name-container {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
</style>
