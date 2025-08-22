<template>
    <main class="container">
        <DynamicContent>
            <hgroup>
                <p class="chapter">DOCS</p>
                <h2>Public HTTP API</h2>
                <p>
                    <span class="mdi mdi-information-outline" aria-hidden="true"></span>
                    The API specification can change at any time; we cannot always guarantee backward compatibility.
                </p>
            </hgroup>

            <hr />
            <section aria-labelledby="docs-heading">
                <h2 id="docs-heading" class="sr-only">API Documentation Links</h2>
                <article>
                    <aside>
                        <nav aria-label="API Documentation">
                            <ul role="list">
                                <li role="listitem">
                                    <a href="/api/openapi.json">
                                        <span class="mdi mdi-file-document-outline" aria-hidden="true"></span>
                                        OpenAPI Specification
                                    </a>
                                </li>
                                <li role="listitem">
                                    <a href="/api/docs">
                                        <span class="mdi mdi-api" aria-hidden="true"></span>
                                        Swagger UI
                                    </a>
                                </li>
                                <li role="listitem">
                                    <a href="/api/redoc">
                                        <span class="mdi mdi-book-open-outline" aria-hidden="true"></span>
                                        ReDoc
                                    </a>
                                </li>
                            </ul>
                        </nav>
                    </aside>

                    <footer>
                        <small>
                            <i>
                                Endpoints are rate-limited; abuse is not tolerated and may result in requests being blocked or an IP being
                                banned.
                            </i>
                        </small>
                    </footer>
                </article>
            </section>
        </DynamicContent>
    </main>
</template>

<script setup lang="ts">
import DynamicContent from '../components/DynamicContent.vue';
import { useSeoMeta } from '@unhead/vue';
import { computed } from 'vue';

// ----- SEO Meta -----
const seoTitle = computed(() => {
    return `Docs - Lotkeeper`;
});
const seoDescription = computed(() => {
    return `Complete API documentation for Lotkeeper's WoW auction house statistics and data service.\n\nAccess OpenAPI specs, Swagger UI, and ReDoc.\nIntegrate with our REST API to fetch item prices, market data, and auction statistics programmatically.`;
});
const seoUrl = computed(() => {
    return `https://lotkeeper.net/docs`;
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
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

nav ul {
    list-style: none;
    padding: 0;
    margin: 0;
    gap: 0.25rem;
    text-align: left;
}

nav li {
    margin: 0;
    text-align: left;
}

nav a {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    justify-content: flex-start;
    text-align: left;
    width: fit-content;
}
</style>
