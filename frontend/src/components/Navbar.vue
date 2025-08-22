<template>
    <div class="nav-wrapper" ref="navWrapper">
        <nav class="navbar" :class="{ mobile: isMobile }" ref="navbarEl">
            <!-- Brand -->
            <ul class="brand-ul">
                <li>
                    <router-link to="/" class="brand-link">
                        <span class="banner">
                            <span class="logo"></span>
                            <span class="brand-text lora">Lotkeeper</span>
                        </span>
                    </router-link>
                </li>
            </ul>

            <!-- Desktop: search + links inline -->
            <ul class="desktop-ul" v-if="!isMobile">
                <li class="search-group-container">
                    <details ref="desktopServerRealmDropdown" class="dropdown server-realm-dropdown">
                        <summary>
                            {{ appStore.getSelectedServerRealm()?.realm || 'Select a realm' }}
                        </summary>
                        <ul>
                            <template v-for="serverRealm in serverRealms" :key="serverRealm.server_slug">
                                <li class="server-name">
                                    <small>{{ serverRealm.server }}</small>
                                </li>
                                <li class="realm-name" v-for="realm in serverRealm.realms" :key="realm.realm_slug">
                                    <a href="#" @click.prevent="selectRealm(serverRealm, realm)">
                                        {{ realm.realm }}
                                    </a>
                                </li>
                            </template>
                        </ul>
                    </details>
                    <form role="search" class="search-group" @submit.prevent="handleSearch">
                        <input
                            name="auction-search"
                            :placeholder="appStore.getSelectedServerRealm() ? 'Try Black Lotus...' : 'Select a realm first...'"
                            v-model="searchInput"
                            :disabled="!appStore.getSelectedServerRealm()" />
                        <input name="search-submit" type="submit" value="Search" :disabled="!appStore.getSelectedServerRealm()" />
                    </form>
                </li>
            </ul>

            <ul class="desktop-ul" v-if="!isMobile">
                <li>
                    <router-link to="/docs" class="nav-link" :class="{ active: currentRoute === '/docs' }">
                        <span class="mdi mdi-file-document"></span>
                        <span class="nav-text">Docs</span>
                    </router-link>
                </li>
                <li>
                    <router-link to="/faq" class="nav-link" :class="{ active: currentRoute === '/faq' }">
                        <span class="mdi mdi-frequently-asked-questions"></span>
                        <span class="nav-text">FAQ</span>
                    </router-link>
                </li>
            </ul>

            <!-- Mobile: full-width dropdown panel -->
            <ul class="mobile-ul" v-else>
                <li class="mobile-menu-item">
                    <details @click="onMobileMenuClick" class="dropdown mega" ref="mobileDetails">
                        <summary class="hamburger" aria-label="Toggle navigation"><span class="mdi mdi-menu"></span> Menu</summary>

                        <!-- Full-width fixed panel -->
                        <ul class="mega-panel">
                            <li class="panel-inner">
                                <form role="mobile-search" class="search-group stack" @submit.prevent="handleSearch">
                                    <details ref="mobileServerRealmDropdown" class="dropdown server-realm-dropdown">
                                        <summary>
                                            {{ appStore.getSelectedServerRealm()?.realm || 'Select a realm' }}
                                        </summary>
                                        <ul>
                                            <template v-for="serverRealm in serverRealms" :key="serverRealm.server_slug">
                                                <li class="server-name">
                                                    <small>{{ serverRealm.server }}</small>
                                                </li>
                                                <li class="realm-name" v-for="realm in serverRealm.realms" :key="realm.realm_slug">
                                                    <a href="#" @click.prevent="selectRealm(serverRealm, realm)">
                                                        {{ realm.realm }}
                                                    </a>
                                                </li>
                                            </template>
                                        </ul>
                                    </details>
                                    <input
                                        name="mobile-auction-search"
                                        :placeholder="appStore.getSelectedServerRealm() ? 'Try Black Lotus...' : 'Select a realm first...'"
                                        v-model="searchInput"
                                        :disabled="!appStore.getSelectedServerRealm()" />
                                    <input
                                        name="mobile-search-submit"
                                        type="submit"
                                        value="Search"
                                        :disabled="!appStore.getSelectedServerRealm()" />
                                </form>

                                <div class="nav-menu column big-links">
                                    <hr />
                                    <router-link to="/" class="nav-link" :class="{ active: currentRoute === '/' }" @click="closeMobile">
                                        <span class="mdi mdi-home"></span>
                                        <span class="nav-text"> Home</span>
                                    </router-link>
                                    <router-link
                                        to="/docs"
                                        class="nav-link"
                                        :class="{ active: currentRoute === '/docs' }"
                                        @click="closeMobile">
                                        <span class="mdi mdi-file-document"></span>
                                        <span class="nav-text"> Docs</span>
                                    </router-link>
                                    <router-link
                                        to="/faq"
                                        class="nav-link"
                                        :class="{ active: currentRoute === '/faq' }"
                                        @click="closeMobile">
                                        <span class="mdi mdi-frequently-asked-questions"></span>
                                        <span class="nav-text"> FAQ</span>
                                    </router-link>
                                </div>
                            </li>
                        </ul>
                    </details>
                </li>
            </ul>
        </nav>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import type { ServerRealm, Realm, ServerRealmOption } from '../services/models';
import { API } from '../services/api-service';
import { useAppStore } from '../stores/AppStore';

const appStore = useAppStore();
const router = useRouter();

// Search input state
const searchInput = ref<string>('');

// Set search input from URL query
const setSearchInputFromUrl = () => {
    const itemName = route.query.item_name as string;
    if (itemName) {
        searchInput.value = itemName;
        appStore.setSearchQuery(itemName);
    } else {
        // Don't clear the search input - preserve the store's search query
        searchInput.value = appStore.getSearchQuery();
    }
};

const handleSearch = () => {
    appStore.setSearchQuery(searchInput.value.trim());

    // Get current server/realm
    const selectedServerRealm = appStore.getSelectedServerRealm();
    router.push({
        path: `/ah/${selectedServerRealm.server_slug}/${selectedServerRealm.realm_slug}/search`,
        query: { item_name: searchInput.value.trim() }
    });

    // Close mobile menu if open
    closeMobile();
};

const selectRealm = (serverRealm: ServerRealm, realm: Realm) => {
    const serverRealmOption: ServerRealmOption = {
        server: serverRealm.server,
        server_slug: serverRealm.server_slug,
        realm: realm.realm,
        realm_slug: realm.realm_slug
    };
    appStore.setSelectedServerRealmOption(serverRealmOption);

    // Clear search input when changing realms
    searchInput.value = '';
    appStore.clearSearchQuery();

    // Close the dropdowns
    if (desktopServerRealmDropdown.value) {
        desktopServerRealmDropdown.value.open = false;
    }
    if (mobileServerRealmDropdown.value) {
        mobileServerRealmDropdown.value.open = false;
    }
};

const route = useRoute();
const currentRoute = computed(() => route.path);

// Auto-set server/realm from URL params
const setServerRealmFromUrl = async () => {
    const serverSlug = route.params.serverSlug as string;
    const realmSlug = route.params.realmSlug as string;

    if (serverSlug && realmSlug) {
        try {
            const serverRealmData = await API.serverRealms.getBySlugs(serverSlug, realmSlug);
            // Find the specific realm that matches the realmSlug from the URL
            const targetRealm = serverRealmData.realms.find((r) => r.realm_slug === realmSlug);
            if (targetRealm) {
                const serverRealmOption: ServerRealmOption = {
                    server: serverRealmData.server,
                    server_slug: serverRealmData.server_slug,
                    realm: targetRealm.realm,
                    realm_slug: targetRealm.realm_slug
                };
                appStore.setSelectedServerRealmOption(serverRealmOption);
            }
        } catch (error) {
            console.error('Error setting server/realm from URL:', error);
        }
    }
};

// Reactive isMobile using matchMedia (SSR-safe)
const isMobile = ref(false);
let mq: MediaQueryList | null = null;
const updateIsMobile = () => {
    if (mq) isMobile.value = mq.matches;
};

// Navbar offset measuring
const navbarEl = ref<HTMLElement | null>(null);
const navWrapper = ref<HTMLElement | null>(null);

let ro: ResizeObserver | null = null;
let rafId: number | null = null;

const setNavOffset = () => {
    const host = navWrapper.value ?? navbarEl.value;
    if (!host) return;
    const b = host.getBoundingClientRect();
    const offset = Math.max(0, Math.round(b.bottom));
    document.documentElement.style.setProperty('--nav-offset', `${offset}px`);
};

const scheduleSetNavOffset = () => {
    if (rafId != null) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(setNavOffset);
};

const serverRealms = ref<ServerRealm[]>([]);

const getServerRealms = async () => {
    const data = await API.serverRealms.get();
    serverRealms.value = data;
};

onMounted(async () => {
    // Get server realms in the background
    getServerRealms();

    // Set server/realm from URL if present
    await setServerRealmFromUrl();

    // Set search input from URL if present
    setSearchInputFromUrl();

    if (typeof window !== 'undefined' && 'matchMedia' in window) {
        mq = window.matchMedia('(max-width: 768px)');
        updateIsMobile();
        if ('addEventListener' in mq)
            mq.addEventListener('change', () => {
                updateIsMobile();
                scheduleSetNavOffset();
            });
        else
            (mq as any).addListener?.(() => {
                updateIsMobile();
                scheduleSetNavOffset();
            });
    }

    // observe size changes of the navbar (font load, sticky, etc.)
    if ('ResizeObserver' in window) {
        ro = new ResizeObserver(scheduleSetNavOffset);
        if (navbarEl.value) ro.observe(navbarEl.value);
        if (navWrapper.value) ro.observe(navWrapper.value);
    }

    window.addEventListener('resize', scheduleSetNavOffset, { passive: true });
    window.addEventListener('scroll', scheduleSetNavOffset, { passive: true });

    // initial
    scheduleSetNavOffset();
});

// Watch for route changes to update server/realm and search input
watch(
    () => [route.params.serverSlug, route.params.realmSlug, route.query.item_name],
    async () => {
        await setServerRealmFromUrl();
        setSearchInputFromUrl();
    }
);

onBeforeUnmount(() => {
    if (mq) {
        if ('removeEventListener' in mq) mq.removeEventListener('change', updateIsMobile);
        else (mq as any).removeListener?.(updateIsMobile);
    }
    if (ro) {
        ro.disconnect();
        ro = null;
    }
    window.removeEventListener('resize', scheduleSetNavOffset);
    window.removeEventListener('scroll', scheduleSetNavOffset);
    if (rafId != null) cancelAnimationFrame(rafId);
});

// Close the mobile details when navigating
const mobileDetails = ref<HTMLDetailsElement | null>(null);
const desktopServerRealmDropdown = ref<HTMLDetailsElement | null>(null);
const mobileServerRealmDropdown = ref<HTMLDetailsElement | null>(null);

const closeMobile = () => {
    if (mobileDetails.value?.open) mobileDetails.value.open = false;
};

const onMobileMenuClick = () => {
    // Close the server realm dropdowns
    if (desktopServerRealmDropdown.value) {
        desktopServerRealmDropdown.value.open = false;
    }
    if (mobileServerRealmDropdown.value) {
        mobileServerRealmDropdown.value.open = false;
    }
};
</script>

<style scoped>
/* --- Layout wrappers --- */
.nav-wrapper {
    top: 0;
    z-index: 50;
    background: var(--pico-card-background-color);
    padding: 0.3rem 1rem;
    overflow: visible;
    position: fixed;
    width: 100%;
    border-bottom: 1px solid var(--pico-muted-border-color);
}

nav {
    display: flex;
    align-items: center;
    gap: 1rem;
    font-family: var(--font-figtree);
    font-weight: 600;
    background: var(--pico-card-background-color);
    padding: 0.65rem 1rem;
    overflow: visible;
    font-size: 1.1rem;
}

nav summary {
    border: 1px solid var(--pico-muted-border-color) !important;
}

.server-realm-dropdown li {
    gap: 0.5rem;
}

.server-realm-dropdown li.server-name {
    font-size: 0.95rem;
    font-weight: 400;
    text-transform: uppercase;
}
.server-realm-dropdown li.realm-name {
    font-size: 1rem;
    font-weight: 600;
}

.brand-ul li {
    padding: 0 !important;
}

.desktop-ul li {
    padding-bottom: 0;
    padding-top: 0;
}

.desktop-ul li.search-group-container {
    display: flex;
    align-items: center;
    gap: 0.5rem;

    padding: 0;
    border-radius: 0.5rem;
}

.search-group-container .search-group {
    padding: 1px;
    border-radius: 1rem;
    background-color: var(--pico-form-element-background-color);
    border: 1px solid var(--pico-muted-border-color) !important;
}

details li {
    padding-bottom: 0.3rem !important;
    padding-top: 0.3rem !important;
}

/* --- Brand --- */
.brand-link {
    text-decoration: none;
    display: flex;
    align-items: center;
    justify-content: center;
    align-items: center;
}

.banner {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-weight: 800;
    color: var(--pico-primary);
}

.brand-text {
    background: linear-gradient(
        180deg,
        #e7c158 0%,
        /* highlight */ #e7c158 35%,
        /* bright gold */ #d2a43e 70%,
        /* mid gold */ #a77433 100% /* shadow gold */
    );
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 900;
    letter-spacing: 0.5px;
}

/* --- Desktop groups --- */
.desktop-ul {
    display: flex;
    align-items: center;
}

/* Search group (desktop) */
.search-group[role='search'],
.search-group[role='group'] {
    display: flex;
    max-width: 640px;
    border: 1px solid var(--pico-muted-border-color);
    overflow: hidden;
}

.search-group input {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    min-height: 42px;
}

.desktop-ul .search-group input,
.desktop-ul .search-group {
    border-radius: 0.5rem !important;
}

.search-group {
    height: 100%;
}

.search-group details {
    width: 100%;
}

.search-group input[name='auction-search'] {
    flex: 1;
    min-width: 180px;
    width: 30dvw;
    border-radius: 0 !important;
}

.search-group input[name='mobile-auction-search'] {
    flex: 1;
    min-width: 180px;
    width: 30dvw;
}

.search-group input[name='search-submit'] {
    flex: 0 0 90px;
    border-top-left-radius: 0 !important;
    border-bottom-left-radius: 0 !important;
}

.search-group input[name='mobile-search-submit'] {
    flex: 0 0 90px;
}

/* Links */
.nav-link {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    color: var(--pico-secondary);
    text-decoration: none;
    padding: 0.4rem 0.75rem;
    border-radius: 0.5rem;
}

.nav-link:hover,
.nav-link.active {
    color: var(--pico-primary);
}

.nav-menu.column {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: inherit;
}

.nav-menu.column a {
    display: flex;
    align-items: center;
    justify-content: center;
}

.big-links .nav-link {
    padding: 0.75rem 0.5rem;
    font-size: 1.05rem;
    border-radius: 0.6rem;
    text-align: center;
}

.big-links .nav-link:hover,
.big-links .nav-link.active {
    color: var(--pico-primary);
}

/* --- Mobile only --- */
.mobile-ul {
    display: none;
    margin-left: auto;
    position: relative;
}

/* Hamburger */
.dropdown.mega {
    position: static;
}

.dropdown.mega > summary.hamburger {
    cursor: pointer;
    user-select: none;
    min-width: 3.25rem;
}

.dropdown.mega > summary::-webkit-details-marker {
    display: none;
}

/* Full-width fixed panel (Pico renders a <ul>) */
:root {
    --nav-offset: 64px;
}

/* fallback before JS runs */

.mobile-ul summary {
    height: 44px !important;
}

.dropdown.mega > ul.mega-panel {
    position: fixed;
    inset: var(--nav-offset) 0 0 0;
    /* <- sits directly under navbar */

    border-top: 2px solid var(--pico-muted-border-color);
    border-radius: 0px !important;
    margin: 0;
    z-index: 60;
}

/* Inner content */
.mega-panel > li.panel-inner {
    list-style: none;
    padding: 1rem;
    display: grid;
    gap: 0.9rem;
    margin-top: 1rem;
}

/* Stacked search in panel */
.mega-panel .search-group.stack {
    display: grid;
    gap: 1rem;
    border: none;
    padding: 0;
}

.mega-panel .search-group.stack input {
    width: 100%;
    border: 1px solid var(--pico-muted-border-color) !important;
    border-radius: 0.5rem;
    min-height: 44px;
}

details {
    margin: 0 !important;
    display: block !important;
}

.mega-panel .search-group.stack details {
    width: 100%;
    border-radius: 0.5rem;
    min-height: 44px;
}

.mobile-menu-item {
    padding: 0;
}

form[role='search'] {
    margin-bottom: 0;
}

/* disable default focus styles */
summary:focus {
    box-shadow: none !important;
    background-color: var(--pico-form-element-background-color) !important;
}

.desktop-ul .dropdown summary {
    min-width: 185px;
    max-width: 185px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 1rem !important;

    border: 1px solid var(--pico-muted-border-color) !important;
}

.mega-panel hr {
    margin: 0.5rem 0;
}

.mobile-ul dropdown summary {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* --- Breakpoints --- */
@media (max-width: 768px) {
    .desktop-ul {
        display: none;
    }

    .mobile-ul {
        display: flex;
    }
}
</style>
