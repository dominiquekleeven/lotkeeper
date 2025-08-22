<template>
    <section class="realm-section">
        <div v-if="error" class="error">
            <span>{{ error }}</span>
        </div>
        <div v-else>
            <DynamicContent>
                <article :aria-busy="ariaBusy(loading)">
                    <div class="server-realm-container" v-for="serverRealm in filteredServerRealms">
                        <p class="chapter">Servers & Realms</p>
                        <hgroup>
                            <p class="chapter"></p>
                            <h4 class="lora">
                                <img :src="SERVER_ICONS[serverRealm.server_slug as keyof typeof SERVER_ICONS]" class="icon-server" />
                                {{ serverRealm.server }}
                            </h4>
                        </hgroup>

                        <div class="grid">
                            <button v-for="realm in serverRealm.realms" @click="selectRealm(serverRealm.server_slug, realm.realm_slug)">
                                {{ realm.realm }}
                            </button>
                        </div>
                    </div>

                    <footer>
                        <small class="text-center"> More servers and realms will be added in the future </small>
                    </footer>
                </article>
            </DynamicContent>
        </div>
    </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { SUPPORTED_SERVERS, SERVER_ICONS } from '../common/constants';
import type { ServerRealm } from '../services/models';
import { computed } from 'vue';
import DynamicContent from './DynamicContent.vue';
import { useAppStore } from '../stores/AppStore';
import type { ServerRealmOption } from '../services/models';
import { ariaBusy } from '../common/util';

const props = defineProps<Props>();

interface Props {
    serverRealms: ServerRealm[];
    loading: boolean;
    error: string;
}

const router = useRouter();
const appStore = useAppStore();

const selectRealm = (serverSlug: string, realmSlug: string) => {
    // Find the server realm object to store
    const serverRealm = props.serverRealms.find((sr) => sr.server_slug === serverSlug);
    if (serverRealm) {
        const realm = serverRealm.realms.find((r) => r.realm_slug === realmSlug);
        if (realm) {
            // Create a ServerRealmOption object
            const serverRealmOption: ServerRealmOption = {
                server: serverRealm.server,
                server_slug: serverRealm.server_slug,
                realm: realm.realm,
                realm_slug: realm.realm_slug
            };
            appStore.setSelectedServerRealmOption(serverRealmOption);
        }
    }
    router.push(`/ah/${serverSlug}/${realmSlug}`);
};

const filteredServerRealms = computed(() => {
    return props.serverRealms.filter((serverRealm) => SUPPORTED_SERVERS.includes(serverRealm.server_slug));
});
</script>

<style scoped>
hgroup p.chapter {
    margin-bottom: 10px !important;
}

hgroup {
    font-weight: 600 !important;
}

hgroup h4 {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-items: center;
    gap: 0.5rem;
    font-weight: 600 !important;
}

.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}

.grid button {
    width: 100%;
}

@media (max-width: 768px) {
    .grid {
        grid-template-columns: 1fr;
        gap: 0.75rem;
    }
}

article[aria-busy='true'] {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    height: 100%;
    min-height: 200px;
    text-align: center;
    font-size: 2em;
}

button {
    font-family: var(--font-figtree) !important;
    font-weight: 600 !important;
}

article[aria-busy='true'] footer {
    display: none;
}
article[aria-busy='true'] div {
    display: none;
}

.server-realm-container {
    padding-bottom: 0.25rem !important;
}

/* Add spacing between server-realm containers */
.server-realm-container:not(:first-child) {
    margin-top: 1rem;
    border-top: 1px solid var(--pico-muted-border-color);
    padding-top: 0.5rem;
}
</style>
