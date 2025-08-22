<template>
    <main class="container">
        <DynamicContent>
            <hgroup>
                <p class="chapter">FAQ</p>
                <h2>Frequently Asked Questions</h2>
                <p>
                    <span class="mdi mdi-comment" aria-hidden="true"></span>
                    Answers to the most common questions about Lotkeeper – a WoW auction house statistics tool
                </p>
            </hgroup>

            <hr />

            <section aria-labelledby="faq-heading">
                <h2 id="faq-heading" class="sr-only">Questions and Answers</h2>
                <article>
                    <dl class="faq-list" role="list">
                        <div class="faq-item" role="listitem">
                            <dt id="faq-1">What is Lotkeeper?</dt>
                            <dd aria-labelledby="faq-1">
                                Lotkeeper is a <strong>WoW auction house analytics tool</strong>. It lets players search for items, check
                                real-time and historical prices, analyze trends, and discover profitable gold-making opportunities across
                                supported servers and realms.
                            </dd>
                        </div>

                        <div class="faq-item" role="listitem">
                            <dt id="faq-2">Why are only buyout prices and auction statistics shown?</dt>
                            <dd aria-labelledby="faq-2">
                                Buyout prices represent the most accurate reflection of the market. Bid prices are often artificially set
                                low to gain auction visibility, which distorts real value. By focusing exclusively on buyout auctions,
                                Lotkeeper ensures <strong>reliable WoW market price tracking</strong> and enables advanced outlier detection
                                for cleaner data. <br /><br />
                                <b>Note:</b> Bid auctions are included in total auction and quantity counts but are excluded from price
                                statistics.
                            </dd>
                        </div>

                        <div class="faq-item" role="listitem">
                            <dt id="faq-3">How frequently is the auction house data updated?</dt>
                            <dd aria-labelledby="faq-3">
                                Lotkeeper updates auction data on an <strong>hourly basis</strong>. If a server or realm is temporarily
                                unavailable, updates may be delayed, but data is refreshed as soon as scans resume.
                            </dd>
                        </div>

                        <div class="faq-item" role="listitem">
                            <dt id="faq-4">How long is historical auction data stored?</dt>
                            <dd aria-labelledby="faq-4">
                                Active auctions refresh every hour, while <strong>historical price data</strong> (such as item price history
                                and trends) is stored for up to one year. Retention periods may be adjusted in the future as Lotkeeper
                                expands.
                            </dd>
                        </div>

                        <div class="faq-item" role="listitem">
                            <dt id="faq-5">How does Lotkeeper detect and filter outliers?</dt>
                            <dd aria-labelledby="faq-5">
                                To prevent skewed results, Lotkeeper applies <strong>Mean Absolute Deviation (MAD)</strong> and
                                <strong>Interquartile Range (IQR)</strong> methods. These statistical techniques filter out unrealistic
                                pricing and ensure that displayed WoW auction house data is fair, accurate, and actionable.
                            </dd>
                        </div>

                        <div class="faq-item" role="listitem">
                            <dt id="faq-6">How is the auction data collected?</dt>
                            <dd aria-labelledby="faq-6">
                                Lotkeeper uses a <strong>custom WoW addon</strong> that scans the auction house every hour. The scanned data
                                is sent to our back-end API where it is processed, filtered, and stored for use in price tracking and
                                analytics.
                            </dd>
                        </div>

                        <div class="faq-item" role="listitem">
                            <dt id="faq-7">Which WoW servers does Lotkeeper support?</dt>
                            <dd aria-labelledby="faq-7">
                                Currently, Lotkeeper supports <strong>Project Epoch</strong>. Planned expansions include additional WoW
                                private servers such as:
                                <ul>
                                    <li>ChromieCraft</li>
                                    <li>Ascension</li>
                                </ul>
                                As data ingestion reliability improves, more realms will be added.
                            </dd>
                        </div>

                        <div class="faq-item" role="listitem">
                            <dt id="faq-8">How can I use Lotkeeper to improve my WoW gold-making strategies?</dt>
                            <dd aria-labelledby="faq-8">
                                Lotkeeper helps players identify <strong>profitable items</strong>, track
                                <strong>price fluctuations</strong>, and analyze <strong>market demand</strong>. Use historical charts to
                                spot seasonal trends, time purchases for maximum profit, and sell when demand peaks to maximize gold
                                earnings.
                            </dd>
                        </div>

                        <div class="faq-item" role="listitem">
                            <dt id="faq-9">Is Lotkeeper compatible with auction house addons like TSM (TradeSkillMaster)?</dt>
                            <dd aria-labelledby="faq-9">
                                Yes. Lotkeeper is independent but complements <strong>TradeSkillMaster (TSM)</strong> and similar addons
                                such as <strong>Auctionator and Auctioneer</strong> by providing a web-based overview of item prices,
                                trends, and statistics. This data can enhance your in-game trading and crafting decisions.
                            </dd>
                        </div>

                        <div class="faq-item" role="listitem">
                            <dt id="faq-10">What statistical methods are used for WoW price analysis?</dt>
                            <dd aria-labelledby="faq-10">
                                Lotkeeper combines <strong>MAD (Mean Absolute Deviation)</strong>,
                                <strong>IQR (Interquartile Range)</strong>, and median-based filtering to remove unreliable outliers. We
                                calculate medians, percentiles, and trend lines to provide
                                <strong>trustworthy auction house price insights</strong>.
                            </dd>
                        </div>

                        <div class="faq-item" role="listitem">
                            <dt id="faq-11">Does Lotkeeper provide an API for developers?</dt>
                            <dd aria-labelledby="faq-11">
                                Yes! Lotkeeper has a free and open <strong>REST API</strong> for developers. It offers access to auction
                                listings, item data, and market statistics. The API supports filtering by
                                <strong>server, realm, item type, and item quality</strong>, making it ideal for building bots, Discord
                                integrations, or custom gold-making tools.
                            </dd>
                        </div>

                        <div class="faq-item" role="listitem">
                            <dt id="faq-12">Is Lotkeeper free to use?</dt>
                            <dd aria-labelledby="faq-12">
                                Lotkeeper is <strong>100% free</strong> for all supported realms. Players can search auctions, analyze
                                markets, and access historical WoW price data at no cost. In the future, optional premium features may be
                                added, but the core service remains free.
                            </dd>
                        </div>

                        <div class="faq-item" role="listitem">
                            <dt id="faq-13">Can I use Lotkeeper on mobile devices?</dt>
                            <dd aria-labelledby="faq-13">
                                Yes. Lotkeeper is fully <strong>mobile-friendly</strong> and responsive. Whether on desktop, tablet, or
                                smartphone, you can check auction prices, monitor market trends, and plan trades on the go.
                            </dd>
                        </div>

                        <div class="faq-item" role="listitem">
                            <dt id="faq-14">How accurate is Lotkeeper’s pricing data?</dt>
                            <dd aria-labelledby="faq-14">
                                Thanks to <strong>hourly scanning</strong> and advanced filtering algorithms, Lotkeeper’s pricing data is
                                highly accurate. Outliers are removed, and only buyout auctions are used to ensure
                                <strong>trustworthy WoW market insights</strong>.
                            </dd>
                        </div>

                        <div class="faq-item" role="listitem">
                            <dt id="faq-15">What makes Lotkeeper different from other WoW auction house tools?</dt>
                            <dd aria-labelledby="faq-15">
                                Lotkeeper focuses on <strong>user experience and accessibility</strong>. While many tools overwhelm users
                                with raw data, Lotkeeper offers a clean interface, detailed price analysis, and reliable statistics. It’s
                                designed to help both casual players and serious traders succeed in WoW’s auction house economy.
                            </dd>
                        </div>
                    </dl>
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
    return `Frequently Asked Questions - Lotkeeper`;
});
const seoDescription = computed(() => {
    return `Frequently asked questions about Lotkeeper's WoW auction house statistics and data service.\n\nLearn about data updates, pricing accuracy, outlier detection, and how our auction scanning works.`;
});
const seoUrl = computed(() => {
    return `https://lotkeeper.net/faq`;
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
/* Screen reader only utility class */
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

.faq-list {
    margin: 0;
    padding: 0;
}

.faq-item {
    margin-bottom: 2rem;
}

.faq-item:last-child {
    margin-bottom: 0;
}

.faq-list dt {
    font-weight: bold;
    margin-bottom: 0.5rem;
    color: var(--primary);
    font-size: 1.1em;
}

.faq-list dd {
    margin-left: 0;
    line-height: 1.6;
    margin-bottom: 0;
}

/* Focus styles for keyboard navigation */
.faq-list dt:focus {
    outline: 2px solid var(--primary);
    outline-offset: 2px;
    border-radius: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    .faq-list dt {
        border-bottom: 1px solid currentColor;
        padding-bottom: 0.25rem;
    }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    .faq-list dt:focus {
        transition: none;
    }
}
</style>
