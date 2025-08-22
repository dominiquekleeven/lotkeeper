<template>
    <main class="container">
        <div v-if="serverRealmError">
            <span>{{ serverRealmError }}</span>
        </div>
        <div v-else>
            <DynamicContent>
                <hgroup>
                    <p class="chapter">Auction House</p>
                    <h1 :aria-busy="ariaBusy(serverRealmLoading)">
                        {{ serverRealm?.server }} <span v-if="realmName">• {{ realmName }} </span>
                    </h1>

                    <p>
                        <span :aria-busy="ariaBusy(realmActivityHourlySummaryLoading)">
                            <span v-if="lastUpdated">Last scan {{ formatRelativeTime(lastUpdated) }}</span>
                            <span v-if="(realmActivityHourlySummaryError || !lastUpdated) && !realmActivityHourlySummaryLoading"
                                >Last scan unknown</span
                            >
                        </span>
                    </p>
                </hgroup>

                <hr />
                <section>
                    <div class="grid">
                        <article class="stat-card">
                            <div class="stat-header">
                                <p class="chapter">Total Buyout Auctions</p>
                            </div>
                            <div class="stat-content">
                                <span v-if="realmActivityHourlySummaryError" class="stat-error">{{ realmActivityHourlySummaryError }}</span>
                                <h3 v-else class="stat-number" :aria-busy="ariaBusy(realmActivityHourlySummaryLoading)">
                                    <span v-if="lastRealmActivityHourlySummary">{{
                                        formatter.format(lastRealmActivityHourlySummary?.total_auctions)
                                    }}</span>
                                </h3>
                            </div>
                            <div class="stat-footer">
                                <p
                                    v-if="auctionsTrend"
                                    :class="[
                                        'stat-trend',
                                        auctionsTrend.isNeutral ? 'neutral' : auctionsTrend.isPositive ? 'positive' : 'negative'
                                    ]">
                                    <span v-if="auctionsTrend.isPositive" class="mdi mdi-trending-up"></span>
                                    <span v-else-if="auctionsTrend.isNeutral" class="mdi mdi-minus"></span>
                                    <span v-else class="mdi mdi-trending-down"></span>
                                    <span>{{ auctionsTrend.percentage }}% vs 24h ago</span>
                                </p>
                                <p v-else class="stat-trend neutral">
                                    <span class="text-empty">empty</span>
                                </p>
                            </div>
                        </article>
                        <article class="stat-card">
                            <div class="stat-header">
                                <p class="chapter">Total Buyout Value</p>
                            </div>
                            <div class="stat-content">
                                <span v-if="realmActivityHourlySummaryError" class="stat-error">{{ realmActivityHourlySummaryError }}</span>
                                <h3 v-else class="stat-number" :aria-busy="ariaBusy(realmActivityHourlySummaryLoading)">
                                    <span class="stat-number-value" v-if="lastRealmActivityHourlySummary"
                                        >{{ formatter.format(getGoldValue(lastRealmActivityHourlySummary?.total_market_value)) }}
                                        <span class="icon-gold"></span
                                    ></span>
                                </h3>
                            </div>
                            <div class="stat-footer">
                                <p
                                    v-if="marketValueTrend"
                                    :class="[
                                        'stat-trend',
                                        marketValueTrend.isNeutral ? 'neutral' : marketValueTrend.isPositive ? 'positive' : 'negative'
                                    ]">
                                    <span v-if="marketValueTrend.isPositive" class="mdi mdi-trending-up"></span>
                                    <span v-else-if="marketValueTrend.isNeutral" class="mdi mdi-minus"></span>
                                    <span v-else class="mdi mdi-trending-down"></span>
                                    <span>{{ marketValueTrend.percentage }}% vs 24h ago</span>
                                </p>
                                <p v-else class="stat-trend neutral">
                                    <span class="text-empty">empty</span>
                                </p>
                            </div>
                        </article>
                    </div>
                </section>
                <hr />

                <Chart
                    :data="chartData"
                    :height="500"
                    :show-legend="true"
                    :show-data-zoom="true"
                    :show-toolbox="false"
                    x-axis-type="time"
                    :smooth="true"
                    :area-style="true"
                    :dark-theme="true"
                    mobile-time-range="1 day"
                    default-time-range="7 days"
                    :is-loading="realmActivityHourlySummaryLoading"
                    chapter="Charts"
                    title="Realm Activity"
                    subtitle="Auction house activity trends"
                    @chart-click="handleChartClick"
                    @legend-change="handleLegendChange" />
            </DynamicContent>
        </div>
    </main>
    <div style="margin-bottom: 4rem"></div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';
import { API } from '../services/api-service';
import Chart from '../components/Chart.vue';
import { onMounted, ref, computed, watch } from 'vue';
import type { AuctionRealmActivityHourlySummary, ServerRealm } from '../services/models';
import type { ChartData } from '../components/Chart.vue';
import DynamicContent from '../components/DynamicContent.vue';
import { useAppStore } from '../stores/AppStore';
import { ariaBusy, formatRelativeTime, getEpochTimestamp } from '../common/util';
import { useSeoMeta } from '@unhead/vue';
import FactionIcon from '../components/FactionIcon.vue';

const appStore = useAppStore();

const route = useRoute();
const serverSlug = computed(() => route.params.serverSlug as string);
const realmSlug = computed(() => route.params.realmSlug as string);
const serverRealm = ref<ServerRealm | null>(null);
const serverRealmLoading = ref(true);
const serverRealmError = ref('');

const realmActivityHourlySummary = ref<AuctionRealmActivityHourlySummary[]>([]);
const realmActivityHourlySummaryLoading = ref(true);
const realmActivityHourlySummaryError = ref('');
const lastUpdated = ref<number>(0);
const lastRealmActivityHourlySummary = ref<AuctionRealmActivityHourlySummary | null>(null);
const formatter = new Intl.NumberFormat('en', { useGrouping: true });
const calculateTrend = (property: keyof AuctionRealmActivityHourlySummary) => {
    if (!realmActivityHourlySummary.value || realmActivityHourlySummary.value.length < 2) {
        return null;
    }

    const current = realmActivityHourlySummary.value[realmActivityHourlySummary.value.length - 1];
    const yesterday = realmActivityHourlySummary.value[realmActivityHourlySummary.value.length - 25];

    if (!yesterday) return null;

    const change = current[property] - yesterday[property];
    const percentage = yesterday[property] === 0 ? 0 : (change / yesterday[property]) * 100;

    return {
        percentage: Math.round(percentage * 10) / 10,
        isPositive: change > 0,
        isNeutral: change === 0,
        isNegative: change < 0
    };
};
const auctionsTrend = computed(() => calculateTrend('total_auctions'));
const marketValueTrend = computed(() => calculateTrend('total_market_value'));

// Find the current realm based on the URL parameter
const currentRealm = computed(() => {
    if (!serverRealm.value || !realmSlug.value) return null;
    return serverRealm.value.realms.find((r) => r.realm_slug === realmSlug.value) || null;
});

// Fallback: get realm name directly from URL if currentRealm is not found
const realmName = computed(() => {
    if (currentRealm.value) {
        return currentRealm.value.realm;
    }
});

const getGoldValue = (value: number) => {
    return Math.floor(value / 10000);
};

const chartData = computed((): ChartData[] => {
    if (!realmActivityHourlySummary.value || realmActivityHourlySummary.value.length === 0) {
        return [];
    }

    return [
        {
            name: 'Total Auctions',
            data: realmActivityHourlySummary.value.map((item) => [new Date(item.ts).getTime(), item.total_auctions]),
            color: '#64b5f6',
            selected: true
        },
        {
            name: 'Total Quantity',
            data: realmActivityHourlySummary.value.map((item) => [new Date(item.ts).getTime(), item.total_quantity]),
            color: '#81c784',
            selected: false
        },
        {
            name: 'Total Market Value',
            data: realmActivityHourlySummary.value.map((item) => [new Date(item.ts).getTime(), getGoldValue(item.total_market_value)]),
            color: '#ffb74d',
            selected: false
        }
    ];
});

const handleChartClick = (params: any) => {};

const handleLegendChange = (params: any) => {};

onMounted(async () => {
    await _loadData();
});

// Watch for route changes to reload data when realm changes
watch(
    () => [serverSlug.value, realmSlug.value],
    async () => {
        await _loadData();
    }
);

const handleServerRealmResult = (result: PromiseSettledResult<any>) => {
    if (result.status === 'fulfilled') {
        serverRealm.value = result.value;
    } else {
        serverRealmError.value = result.reason instanceof Error ? result.reason.message : 'An error occurred';
    }
    serverRealmLoading.value = false;
};

const handleActivitySummaryResult = (result: PromiseSettledResult<any>) => {
    if (result.status === 'fulfilled') {
        const data = result.value;
        realmActivityHourlySummary.value = data;

        if (data.length === 0) {
            lastRealmActivityHourlySummary.value = null;
            lastUpdated.value = null;
            realmActivityHourlySummaryError.value = 'No data found';
        } else {
            lastRealmActivityHourlySummary.value = data[data.length - 1];
            lastUpdated.value = lastRealmActivityHourlySummary.value.ts;
        }
    } else {
        realmActivityHourlySummaryError.value = result.reason instanceof Error ? result.reason.message : 'An error occurred';
    }
    realmActivityHourlySummaryLoading.value = false;
};

const _loadData = async () => {
    serverRealmLoading.value = true;
    realmActivityHourlySummaryLoading.value = true;

    serverRealmError.value = '';
    realmActivityHourlySummaryError.value = '';

    const fromTimestamp = getEpochTimestamp(31);
    const toTimestamp = getEpochTimestamp();

    const [serverRealmResult, activitySummaryResult] = await Promise.allSettled([
        API.serverRealms.getBySlugs(serverSlug.value, realmSlug.value),
        API.auctionDatapoints.getRealmActivityHourlySummary(serverSlug.value, realmSlug.value, fromTimestamp, toTimestamp)
    ]);
    handleServerRealmResult(serverRealmResult);
    handleActivitySummaryResult(activitySummaryResult);
};

// ----- SEO Meta -----
const seoServer = computed(() => serverRealm.value?.server ?? 'WoW');
const seoRealm = computed(() => realmName.value || 'Realm');
const seoTitle = computed(() => {
    return `${seoServer.value} • ${seoRealm.value} - WoW Auction House Statistics - Lotkeeper`;
});
const seoDescription = computed(() => {
    return `WoW Auction house statistics and data for ${seoServer.value} • ${seoRealm.value}.\n\nTrack auction trends, market values, and trading activity with comprehensive statistics and interactive charts.`;
});
const seoUrl = computed(() => {
    return `https://lotkeeper.net/ah/${serverSlug.value}/${realmSlug.value}`;
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
.stat-card {
    background: var(--pico-card-background-color);
    border: 1px solid var(--pico-card-border-color);
    border-radius: var(--pico-border-radius);
    padding: 1.5rem;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
    min-height: 95px;
}

.stat-header .chapter {
    margin-bottom: 0.5rem;
}

.stat-content {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.stat-number {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-family: var(--font-figtree) !important;
    font-size: 2rem;
    font-weight: 700;
    color: var(--pico-heading-color);
    margin: 0;
    line-height: 1;
}

.stat-trend {
    font-size: 0.875rem;
    font-weight: 500;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.stat-trend.positive {
    color: #10b981;
}

.stat-trend.negative {
    color: #ef4444;
}

.stat-trend.neutral {
    color: var(--pico-muted-color) !important;
}

.stat-footer {
    font-size: 0.875rem;
    font-weight: 500;
    margin: 0;
    margin-top: 0.5rem;
}

.icon-gold {
    min-width: 24px;
    width: 24px;
    height: 24px;
}

.stat-number-value {
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

@media (max-width: 768px) {
    .stat-card {
        padding: 1rem;
        margin-bottom: 0.25rem;
    }

    .icon-gold {
        min-width: 16px;
        width: 16px;
        height: 16px;
    }

    .stat-number {
        font-size: 1.5rem;
    }

    .stat-header {
        margin-bottom: 0.75rem;
    }
}
</style>
