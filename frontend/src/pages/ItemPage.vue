<template>
    <main class="container">
        <DynamicContent>
            <section>
                <a @click="goBack" class="chapter"> <span class="mdi mdi-arrow-left"></span> Back </a>

                <p :aria-busy="ariaBusy(activityDataLoading)" class="time-text muted"
                    ><span v-if="lastUpdated">Last updated {{ formatRelativeTime(lastUpdated) }}</span
                    ><span v-if="activityDataLoading && !lastUpdated" class="text-empty">empty</span>
                    <span class="time-text muted" v-if="!activityDataLoading && !lastUpdated"
                        >Item was seen, but no auction data was captured</span
                    >
                </p>

                <div class="cards-container">
                    <!-- Top row: Item details and stacked smaller cards -->
                    <div class="top-row">
                        <div :aria-busy="itemLoading" class="item-card">
                            <template v-if="itemLoading"> </template>

                            <template v-else-if="itemError">
                                <div class="error-message">
                                    <h3><span class="mdi mdi-alert-outline"></span> {{ itemError }}</h3>
                                </div>
                            </template>

                            <template v-else-if="item">
                                <div class="card-header">
                                    <WowIcon :icon="item.icon" :size="48" />
                                    <span :class="getQualityColor(item.quality)">{{ item.name }}</span>
                                </div>

                                <div class="card-content">
                                    <div class="card-row">
                                        <span class="card-label">Level</span>
                                        <span class="card-value">{{ item.level }}</span>
                                    </div>
                                    <div class="card-row">
                                        <span class="card-label">Quality</span>
                                        <span class="card-value">{{ QUALITY_LEVELS[item.quality] }}</span>
                                    </div>
                                    <div class="card-row">
                                        <span class="card-label">Category</span>
                                        <span class="card-value">{{ item.class_name }}</span>
                                    </div>
                                    <div class="card-row">
                                        <span class="card-label">Max Stack</span>
                                        <span class="card-value">{{ item.max_stack_size }}</span>
                                    </div>
                                    <div class="card-row">
                                        <span class="card-label">Unit Vendor Price</span>
                                        <span class="card-value" v-if="(item.vendor_price ?? 0) === 0">No sell price</span>
                                        <span class="card-value" v-else v-html="getFormattedPriceHtml(item.vendor_price ?? 0)"></span>
                                    </div>
                                </div>
                            </template>
                        </div>

                        <div class="stacked-cards">
                            <div class="auction-card market-value-card">
                                <p class="chapter">Total Market Value</p>
                                <div class="card-content">
                                    <div class="market-value-list">
                                        <div class="market-value-item">
                                            <span class="market-value-label">
                                                Unfiltered
                                                <span data-tooltip="Sum of all active buyouts without any outlier filtering"
                                                    ><span class="mdi mdi-information-outline"></span
                                                ></span>
                                            </span>
                                            <span
                                                class="market-value-price"
                                                v-html="getFormattedPriceHtml(lastKnownActivityData?.total_market_value ?? 0)"></span>
                                        </div>
                                        <div class="market-value-item">
                                            <span class="market-value-label">
                                                Filtered
                                                <span data-tooltip="Market value after per-item outlier filtering"
                                                    ><span class="mdi mdi-information-outline"></span
                                                ></span>
                                            </span>
                                            <span
                                                class="market-value-price"
                                                v-html="getFormattedPriceHtml(lastKnownActivityData?.estimated_market_value ?? 0)"></span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="auction-card availability-card">
                                <p class="chapter">Item Availability</p>
                                <div class="card-content">
                                    <div class="card-row">
                                        <span class="card-label">Auctions</span>
                                        <span class="card-value">{{ lastKnownActivityData?.total_auctions ?? '—' }}</span>
                                    </div>
                                    <div class="card-row">
                                        <span class="card-label">Quantity</span>
                                        <span class="card-value">{{ lastKnownActivityData?.total_quantity ?? '—' }}</span>
                                    </div>
                                    <div class="card-row">
                                        <span class="card-label">Avg. Stack</span>
                                        <span class="card-value">{{ averageStackSize }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="bottom-row">
                        <div class="auction-card pricing-card">
                            <p class="chapter">Unit Price</p>

                            <div class="card-content">
                                <div class="card-row">
                                    <span class="card-label">Min</span>
                                    <span
                                        class="card-value"
                                        v-html="getFormattedPriceHtml(lastKnownPricingData?.min_buyout_price ?? 0)"></span>
                                </div>
                                <div class="card-row">
                                    <span class="card-label">Max</span>
                                    <span
                                        class="card-value"
                                        v-html="getFormattedPriceHtml(lastKnownPricingData?.max_buyout_price ?? 0)"></span>
                                </div>
                                <div class="card-row">
                                    <span class="card-label">Avg</span>
                                    <span
                                        class="card-value"
                                        v-html="getFormattedPriceHtml(lastKnownPricingData?.avg_buyout_price ?? 0)"></span>
                                </div>
                                <div class="card-row">
                                    <span class="card-label">Median</span>
                                    <span
                                        class="card-value"
                                        v-html="getFormattedPriceHtml(lastKnownPricingData?.median_buyout_price ?? 0)"></span>
                                </div>
                            </div>
                        </div>

                        <div class="stacked-cards">
                            <div class="auction-card percentiles-card">
                                <p class="chapter">Unit Price Percentiles</p>
                                <div class="card-content">
                                    <div class="card-row">
                                        <span class="card-label">10th</span>
                                        <span
                                            class="card-value"
                                            v-html="getFormattedPriceHtml(lastKnownPricingData?.p10_buyout_price ?? 0)"></span>
                                    </div>
                                    <div class="card-row">
                                        <span class="card-label">25th</span>
                                        <span
                                            class="card-value"
                                            v-html="getFormattedPriceHtml(lastKnownPricingData?.p25_buyout_price ?? 0)"></span>
                                    </div>
                                    <div class="card-row">
                                        <span class="card-label">75th</span>
                                        <span
                                            class="card-value"
                                            v-html="getFormattedPriceHtml(lastKnownPricingData?.p75_buyout_price ?? 0)"></span>
                                    </div>
                                    <div class="card-row">
                                        <span class="card-label">90th</span>
                                        <span
                                            class="card-value"
                                            v-html="getFormattedPriceHtml(lastKnownPricingData?.p90_buyout_price ?? 0)"></span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
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
                :is-loading="pricingDataLoading"
                :currency-unit="bestUnit"
                chapter="Charts"
                title="Unit Price"
                subtitle="Auction house price trends"
                @chart-click="handleChartClick"
                @legend-change="handleLegendChange" />
        </DynamicContent>
    </main>
    <div style="margin-bottom: 4rem"></div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router';
import DynamicContent from '../components/DynamicContent.vue';
import { API } from '../services/api-service';
import { Item, AuctionMarketActivityHourlySummary, AuctionPriceHourlySummary } from '../services/models';
import { ref, onMounted, computed, onUnmounted } from 'vue';
import { useAppStore } from '../stores/AppStore';
import {
    getQualityColor,
    getFormattedPriceHtml,
    getEpochTimestamp,
    formatRelativeTime,
    ariaBusy,
    getIconUrl,
    fromSlug
} from '../common/util';
import { QUALITY_LEVELS } from '../common/constants';
import type { ChartData } from '../components/Chart.vue';
import Chart from '../components/Chart.vue';
import WowIcon from '../components/WowIcon.vue';
import { useSeoMeta } from '@unhead/vue';

const router = useRouter();
const route = useRoute();
const appStore = useAppStore();

const item_id = route.params.id as string;
const item_slug = route.params.itemSlug as string;
const serverSlug = computed(() => (route.params.serverSlug as string) || appStore.getSelectedServerSlug());
const realmSlug = computed(() => (route.params.realmSlug as string) || appStore.getSelectedRealmSlug());

const backTo = computed(() => route.query.back);
const item = ref<Item | null>(null);
const itemLoading = ref<boolean>(false);
const itemError = ref<string>('');

const pricingData = ref<AuctionPriceHourlySummary[]>([]);
const pricingDataLoading = ref<boolean>(false);
const pricingDataError = ref<string>('');
const lastKnownPricingData = ref<AuctionPriceHourlySummary | null>(null);
const activityData = ref<AuctionMarketActivityHourlySummary[]>([]);
const activityDataLoading = ref<boolean>(false);
const activityDataError = ref<string>('');
const lastKnownActivityData = ref<AuctionMarketActivityHourlySummary | null>(null);
const lastUpdated = ref<number>(0);
const averageStackSize = computed(() => {
    const a = lastKnownActivityData.value;
    if (!a || !a.total_auctions) return '—';
    const avg = a.total_quantity / a.total_auctions;
    return Number.isFinite(avg) ? Math.round(avg).toString() : '—';
});

onMounted(async () => {
    await loadData();
});

const handleItemResult = (result: PromiseSettledResult<any>) => {
    if (result.status === 'fulfilled') {
        const items = result.value;
        if (items.data.length === 0) {
            itemError.value = 'Item not found';
        } else {
            item.value = items.data[0];
            item.value.class_name = item.value.class_name.charAt(0).toUpperCase() + item.value.class_name.slice(1);
        }
    } else {
        console.error('Error fetching item:', result.reason);
        itemError.value = 'Error fetching item';
    }
    itemLoading.value = false;
};

const handlePricingResult = (result: PromiseSettledResult<any>) => {
    if (result.status === 'fulfilled') {
        const data = result.value;
        if (data.length < 1) {
            pricingDataError.value = 'No pricing data found';
        } else {
            pricingData.value = data;
            lastKnownPricingData.value = data[data.length - 1];
        }
    } else {
        console.error('Error fetching item pricing:', result.reason);
        pricingDataError.value = 'Error fetching item pricing';
    }
    pricingDataLoading.value = false;
};

const handleActivityResult = (result: PromiseSettledResult<any>) => {
    if (result.status === 'fulfilled') {
        const data = result.value;
        if (data.length < 1) {
            activityDataError.value = 'No activity data found';
        } else {
            activityData.value = data;
            lastKnownActivityData.value = data[data.length - 1];
            lastUpdated.value = lastKnownActivityData.value.timestamp;
        }
    } else {
        console.error('Error fetching item activity:', result.reason);
        activityDataError.value = 'Error fetching item activity';
    }
    activityDataLoading.value = false;
};

const loadData = async () => {
    itemLoading.value = true;
    pricingDataLoading.value = true;
    activityDataLoading.value = true;

    itemError.value = '';
    pricingDataError.value = '';
    activityDataError.value = '';
    const fromTimestamp = getEpochTimestamp(31);
    const toTimestamp = getEpochTimestamp();
    const item_filter = { id: parseInt(item_id) };

    const [itemResult, pricingResult, activityResult] = await Promise.allSettled([
        API.items.getFiltered(serverSlug.value!, realmSlug.value!, item_filter),
        API.auctionDatapoints.getPriceHourlySummary(serverSlug.value!, realmSlug.value!, parseInt(item_id), fromTimestamp, toTimestamp),
        API.auctionDatapoints.getItemActivityHourlySummary(
            serverSlug.value!,
            realmSlug.value!,
            parseInt(item_id),
            fromTimestamp,
            toTimestamp
        )
    ]);
    handleItemResult(itemResult);
    handlePricingResult(pricingResult);
    handleActivityResult(activityResult);
};

const goBack = () => {
    if (backTo.value) {
        router.push(backTo.value as string);
    } else if (window.history.length > 1) {
        router.go(-1);
    } else {
        router.push('/');
    }
};

const handleChartClick = (params: any) => {};

const handleLegendChange = (params: any) => {};

const getBestUnit = (prices: number[]) => {
    const maxPrice = Math.max(...prices);
    if (maxPrice >= 10000) return 'gold';
    if (maxPrice >= 100) return 'silver';
    return 'copper';
};

const bestUnit = computed(() => {
    if (!pricingData.value || pricingData.value.length === 0) {
        return 'copper';
    }
    return getBestUnit(pricingData.value.map((item) => item.p10_buyout_price));
});

const chartData = computed((): ChartData[] => {
    if (!pricingData.value || pricingData.value.length === 0) {
        return [];
    }

    const bestUnitValue = bestUnit.value;
    const bestUnitDivisor = bestUnitValue === 'gold' ? 10000 : bestUnitValue === 'silver' ? 100 : 1;

    return [
        {
            name: 'Min',
            data: pricingData.value.map((item) => [new Date(item.timestamp).getTime(), item.min_buyout_price / bestUnitDivisor]),
            color: '#1f77b4', // Blue
            selected: true
        },
        {
            name: 'Avg',
            data: pricingData.value.map((item) => [new Date(item.timestamp).getTime(), item.avg_buyout_price / bestUnitDivisor]),
            color: '#ff7f0e', // Orange
            selected: false
        },
        {
            name: 'Median',
            data: pricingData.value.map((item) => [new Date(item.timestamp).getTime(), item.median_buyout_price / bestUnitDivisor]),
            color: '#2ca02c', // Green
            selected: false
        },
        {
            name: 'Max',
            data: pricingData.value.map((item) => [new Date(item.timestamp).getTime(), item.max_buyout_price / bestUnitDivisor]),
            color: '#d62728', // Red
            selected: false
        },
        {
            name: '10th',
            data: pricingData.value.map((item) => [new Date(item.timestamp).getTime(), item.p10_buyout_price / bestUnitDivisor]),
            color: '#9467bd', // Purple
            selected: false
        },
        {
            name: '25th',
            data: pricingData.value.map((item) => [new Date(item.timestamp).getTime(), item.p25_buyout_price / bestUnitDivisor]),
            color: '#8c564b', // Brown
            selected: false
        },
        {
            name: '75th',
            data: pricingData.value.map((item) => [new Date(item.timestamp).getTime(), item.p75_buyout_price / bestUnitDivisor]),
            color: '#ffd700', // Yellow
            selected: false
        }
    ];
});

// ----- SEO Meta -----
const seoServer = computed(() => fromSlug(serverSlug.value) ?? 'WoW');
const seoRealm = computed(() => fromSlug(realmSlug.value) ?? 'Realm');
const seoItemName = computed(() => item.value?.name ?? 'Item');
const seoTitle = computed(() => {
    return `${seoItemName.value} - ${seoServer.value} • ${seoRealm.value} - Lotkeeper`;
});
const seoDescription = computed(() => {
    const itemName = seoItemName.value;
    const server = seoServer.value;
    const realm = seoRealm.value;
    return `WoW Auction house pricing and market data for "${itemName}" on ${server} • ${realm}.\n\nView current prices, price trends, availability, and market analysis with interactive charts.`;
});
const seoUrl = computed(() => {
    return `https://lotkeeper.net/ah/${serverSlug.value}/${realmSlug.value}/item/${item_id}/${item_slug}`;
});

useSeoMeta({
    title: seoTitle,
    description: seoDescription,
    ogTitle: seoTitle,
    ogDescription: seoDescription,
    twitterTitle: seoTitle,
    twitterDescription: seoDescription,
    ogUrl: seoUrl,
    twitterUrl: seoUrl,
    ogImage: computed(() => (item.value?.icon ? getIconUrl(item.value.icon) : 'https://lotkeeper.net/images/logo.png')),
    twitterImage: computed(() => (item.value?.icon ? getIconUrl(item.value.icon) : 'https://lotkeeper.net/images/logo.png'))
});
</script>

<style scoped>
.cards-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-top: 1rem;
}

.top-row,
.bottom-row {
    display: flex;
    gap: 1rem;
    align-items: stretch;
    width: 100%;
}

.stacked-cards {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    flex: 1;
    min-width: 0;
}

.item-card,
.pricing-card,
.percentiles-card {
    flex: 1;
    min-width: 0;
}

@media (max-width: 479px) {
    .cards-container {
        gap: 1rem;
        margin-top: 0.75rem;
    }
    .top-row,
    .bottom-row {
        flex-direction: column;
        gap: 1rem;
    }
    .stacked-cards {
        gap: 1rem;
    }
    .item-card,
    .auction-card {
        padding: 0.5rem;
    }
}

@media (min-width: 480px) and (max-width: 767px) {
    .top-row,
    .bottom-row {
        flex-direction: column;
        gap: 0.75rem;
    }
    .stacked-cards {
        gap: 0.75rem;
    }
    .item-card,
    .auction-card {
        padding: 0.75rem;
    }
}

@media (min-width: 768px) and (max-width: 1023px) {
    .top-row {
        flex-direction: row;
        gap: 1rem;
    }
    .bottom-row {
        flex-direction: column;
        gap: 1rem;
    }
}

@media (min-width: 1024px) {
    .top-row,
    .bottom-row {
        flex-direction: row;
        gap: 1rem;
    }
}

@media (min-width: 1200px) {
    .cards-container,
    .top-row,
    .bottom-row,
    .stacked-cards {
        gap: 1.5rem;
    }
}

.item-card,
.auction-card {
    background: var(--pico-card-background-color);
    border: 1px solid var(--pico-muted-border-color);
    border-radius: var(--pico-border-radius);
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    min-height: fit-content;
}

.card-header {
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--pico-muted-border-color);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card-header span {
    margin: 0;
    line-height: 1;
    font-family: var(--font-open-sans) !important;
    font-size: 1.4em;
}

.card-content {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
.card-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
}

.card-label {
    font-weight: 500;
    color: var(--pico-muted-color);
    font-size: 0.9em;
    min-width: 110px;
}

.card-value {
    text-align: right;
    flex: 1;
}

.market-value-list {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
}
.market-value-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
}
.market-value-label {
    font-size: 0.9em;
    color: var(--pico-muted-color);
    font-weight: 500;
}
.market-value-price {
    font-weight: 500;
}

.muted {
    color: var(--pico-muted-color);
}

.time-text {
    width: fit-content;
    margin-bottom: 0;
    padding-bottom: 0;
    line-height: 2;
}

.tip {
    font-size: 0.95em;
    vertical-align: text-bottom;
    margin-left: 0.25rem;
}

.error-message h3 {
    margin: 0;
    line-height: 1;
    font-weight: 500;
}

a {
    cursor: pointer;
}
</style>
