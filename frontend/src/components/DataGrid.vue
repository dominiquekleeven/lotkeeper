<template>
    <DynamicContent>
        <div class="data-grid">
            <!-- Card View (Desktop Grid + Mobile Single Column) -->
            <div v-if="!loading && data && data.length > 0" class="card-view">
                <div
                    v-for="(item, index) in sortedData"
                    :key="getRowKey(item, index)"
                    class="data-card"
                    :class="{ clickable: !!onItemClick }"
                    @click="onItemClick ? handleItemClick(item, index) : null">
                    <div class="card-header">
                        <slot :name="`cell-${columns[0].key}`" :item="item" :value="getValue(item, columns[0].key)" :column="columns[0]">
                            <span v-if="columns[0].formatter" v-html="columns[0].formatter(getValue(item, columns[0].key), item)"></span>
                            <span v-else>{{ getValue(item, columns[0].key) }}</span>
                        </slot>
                    </div>
                    <div class="card-content">
                        <div v-for="column in columns.slice(1)" :key="column.key" class="card-row">
                            <span class="card-label">{{ column.label }}</span>
                            <span class="card-value">
                                <slot :name="`cell-${column.key}`" :item="item" :value="getValue(item, column.key)" :column="column">
                                    <span v-if="column.formatter" v-html="column.formatter(getValue(item, column.key), item)"></span>
                                    <span v-else>{{ getValue(item, column.key) }}</span>
                                </slot>
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="loading-state">
                <span style="font-size: 2rem" aria-busy="true"> </span>
            </div>
        </div>
    </DynamicContent>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import DynamicContent from './DynamicContent.vue';

export interface GridColumn {
    key: string;
    label: string;
    sortable?: boolean;
    formatter?: (value: any, item: any) => string;
}

export interface GridProps {
    data: any[];
    columns: GridColumn[];
    striped?: boolean;
    loading?: boolean;
    rowKey?: string | ((item: any, index: number) => string);
    onItemClick?: (item: any, index: number) => void;
}

const props = withDefaults(defineProps<GridProps>(), {
    striped: true,
    loading: false,
    rowKey: 'id'
});

const emit = defineEmits<{
    sort: [key: string, order: 'asc' | 'desc'];
    'item-click': [item: any, index: number];
}>();

// Computed properties
const sortedData = computed(() => {
    return props.data;
});

// Methods
const getValue = (item: any, key: string) => {
    return key.split('.').reduce((obj, k) => obj?.[k], item);
};

const getRowKey = (item: any, index: number) => {
    if (typeof props.rowKey === 'function') {
        return props.rowKey(item, index);
    }
    return item[props.rowKey] || index;
};

const handleItemClick = (item: any, index: number) => {
    if (props.onItemClick) {
        props.onItemClick(item, index);
    }
    emit('item-click', item, index);
};
</script>

<style scoped>
.data-grid {
    width: 100%;
}

/* Card View */
.card-view {
    display: grid;
    grid-template-columns: repeat(4, 1fr); /* 4-wide grid on desktop */
    gap: 1.5rem;
    margin-bottom: 1rem;
}

.data-card {
    background: var(--pico-card-background-color);
    border: 1px solid var(--pico-muted-border-color);
    border-radius: var(--pico-border-radius);
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    transition: all 0.2s ease;
    cursor: pointer;
}

/* Only apply hover effects on devices that support hover */
@media (hover: hover) and (pointer: fine) {
    .data-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border-color: var(--pico-primary);
    }
}

.data-card.clickable:active {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--pico-muted-border-color);
    line-height: 1.2;
    min-height: 2.4lh; /* Exactly 2 lines */
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
    min-width: 80px;
}

.card-value {
    text-align: right;
    flex: 1;
}

/* Loading State */
.loading-state {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 200px;
}

.loading-state article {
    text-align: center;
}

/* Responsive Design */
@media (min-width: 1201px) and (max-width: 1550px) {
    .card-view {
        grid-template-columns: repeat(3, 1fr); /* 3-wide on medium screens eg laptop*/
    }
}

@media (min-width: 769px) and (max-width: 1200px) {
    .card-view {
        grid-template-columns: repeat(2, 1fr); /* 2-wide on smaller screens eg tablet*/
    }
}

@media (max-width: 768px) {
    .card-view {
        grid-template-columns: 1fr; /* Single column on mobile eg phone*/
        gap: 1rem;
    }
}

@media (max-width: 480px) {
    .data-card {
        padding: 0.75rem;
    }

    .card-content {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.5rem;
    }

    .card-row {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.25rem;
    }

    .card-label {
        min-width: auto;
        font-size: 0.8em;
    }

    .card-value {
        text-align: left;
        font-size: 0.9em;
    }
}

/* Touch-friendly improvements */
@media (hover: none) and (pointer: coarse) {
    th.sortable {
        padding: 1rem 0.5rem;
    }

    .data-card {
        -webkit-tap-highlight-color: transparent;
    }
}
</style>
