import { createApp, nextTick } from 'vue';
import { createPinia } from 'pinia';
import { createRouter, createWebHistory } from 'vue-router';
import { createHead } from '@unhead/vue/client';
import App from './App.vue';

import HomePage from './pages/WipPage.vue';
import NotFoundPage from './pages/NotFoundPage.vue';
import DisclaimerPage from './pages/DisclaimerPage.vue';
import DocsPage from './pages/DocsPage.vue';
import FAQPage from './pages/FAQPage.vue';
import AuctionHousePage from './pages/AuctionHousePage.vue';
import SearchPage from './pages/SearchPage.vue';
import ItemPage from './pages/ItemPage.vue';
import '@mdi/font/css/materialdesignicons.css';
import './styles.css';

const routes = [
    { path: '/', component: HomePage },
    { path: '/disclaimer', component: DisclaimerPage },
    {
        path: '/ah/:serverSlug/:realmSlug',
        component: AuctionHousePage,
        meta: {
            requiresAuth: false,
            pageTitle: 'Auction House'
        }
    },
    { path: '/ah/:serverSlug/:realmSlug/search', component: SearchPage },
    { path: '/ah/:serverSlug/:realmSlug/item/:id/:itemSlug', component: ItemPage },
    { path: '/docs', component: DocsPage },
    { path: '/faq', component: FAQPage },
    { path: '/:pathMatch(.*)*', component: NotFoundPage }
];

const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior(to, from, savedPosition) {
        return nextTick().then(() => {
            return { left: 0, top: 0, behavior: 'instant' };
        });
    }
});

const pinia = createPinia();
const app = createApp(App);
const head = createHead();

app.use(head);
app.use(router);
app.use(pinia);
app.mount('#app');
