<template>
    <main class="container">
        <DynamicContent>
            <section class="intro">
                <hgroup>
                    <h1 class="text-center heading">Lotkeeper</h1>
                    <p class="text-center tagline"> From Lots to Gold </p>
                </hgroup>
                <p class="text-center description">
                    Track auction house prices, spot market trends, and plan your next gold-making strategies
                </p>
            </section>

            <div class="fancy-hr">
                <span class="mdi mdi-treasure-chest-outline"></span>
            </div>
            <section>
                <RealmSelector :serverRealms="serverRealms" :loading="serverRealmsLoading" :error="serverRealmsError" />
            </section>
        </DynamicContent>
    </main>
</template>

<script setup lang="ts">
import DynamicContent from '../components/DynamicContent.vue';
import type { ServerRealm } from '../services/models';
import RealmSelector from '../components/RealmSelector.vue';
import { API } from '../services/api-service';
import { onMounted, ref } from 'vue';

const serverRealms = ref<ServerRealm[]>([]);
const serverRealmsLoading = ref(true);
const serverRealmsError = ref('');

onMounted(async () => {
    try {
        serverRealms.value = await API.serverRealms.get();
        serverRealmsLoading.value = false;
    } catch (error) {
        serverRealmsError.value = error instanceof Error ? error.message : 'An error occurred';
        serverRealmsLoading.value = false;
    }
});
</script>

<style scoped>
hgroup {
    margin-bottom: 0.5rem;
    align-items: center;
}

.heading {
    font-size: 2.5rem;
    font-family: var(--font-lora);
    background: linear-gradient(
        180deg,
        #e7c158 0%,
        /* highlight */ #e7c158 35%,
        /* bright gold */ #d2a43e 50%,
        /* mid gold */ #a77433 100% /* shadow gold */
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 1px;
}

.tagline {
    font-family: var(--font-figtree);
    font-size: 1.2rem;
    letter-spacing: 0.7px;
    font-style: italic;
    line-height: 1.4;
}
.description {
    font-size: 1rem;

    margin-bottom: 0;
}

.divider {
    font-size: 1.4rem;
    color: #e6d27a;
    margin: 0.6rem auto;
}

.intro {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-bottom: 0.5rem;
}

.fancy-hr {
    display: flex;
    align-items: center;
    text-align: center;
    margin: 0.5rem auto;
    color: #e6d27a;
}

.fancy-hr::before,
.fancy-hr::after {
    content: '';
    flex: 1;
    border-bottom: 1px solid #202632;
}

.fancy-hr:not(:empty)::before {
    margin-right: 0.75em;
}
.fancy-hr:not(:empty)::after {
    margin-left: 0.75em;
}

.fancy-hr span {
    font-size: 1.2rem;
    color: var(--pico-primary);
}
</style>
