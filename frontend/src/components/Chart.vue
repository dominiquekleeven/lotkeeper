<template>
    <div class="chart-container">
        <section>
            <div class="header-section">
                <hgroup>
                    <p class="chapter">{{ chapter }}</p>
                    <h2>{{ title }} <span class="mdi mdi-pan-horizontal"></span></h2>
                    <p>{{ subtitle }}</p>
                </hgroup>
                <div class="chart-controls">
                    <details class="dropdown time-range-dropdown" ref="timeRangeDropdown">
                        <summary>{{ selectedTimeRange }}</summary>
                        <ul>
                            <li><a href="#" @click.prevent="selectTimeRange('1 day')">1 day</a></li>
                            <li><a href="#" @click.prevent="selectTimeRange('3 days')">3 days</a></li>
                            <li><a href="#" @click.prevent="selectTimeRange('7 days')">7 days</a></li>
                            <li><a href="#" @click.prevent="selectTimeRange('14 days')">14 days</a></li>
                            <li><a href="#" @click.prevent="selectTimeRange('30 days')">30 days</a></li>
                        </ul>
                    </details>
                </div>
            </div>

            <div class="chart-content">
                <div v-if="loading || props.isLoading" class="loading" :style="{ height: responsiveHeight + 'px' }">
                    <span style="font-size: 2rem" aria-busy="true"> </span>
                </div>
                <div v-else-if="error" class="error">
                    <span>{{ error }}</span>
                </div>
                <div v-else-if="!hasData" class="no-data">
                    <span>No data available</span>
                </div>
                <div v-else class="chart-wrapper">
                    <v-chart
                        ref="chartInstance"
                        :option="chartOption"
                        :style="{ height: responsiveHeight + 'px', width: '100%' }"
                        @click="handleChartClick"
                        @legendselectchanged="handleLegendChange" />
                </div>
            </div>
        </section>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick, onUnmounted } from 'vue';
import { use } from 'echarts/core';
import { SVGRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent, DataZoomComponent, ToolboxComponent } from 'echarts/components';
import VChart from 'vue-echarts';
import { formatCurrencyForChart } from '../common/util';

use([SVGRenderer, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, DataZoomComponent, ToolboxComponent]);

export interface ChartData {
    name: string;
    data: Array<[string | number, number]>;
    color?: string;
    selected?: boolean;
}

export type TimeRangeOption = '1 day' | '3 days' | '7 days' | '14 days' | '30 days';

export interface ChartProps {
    data: ChartData[];
    chapter?: string; // Chapter text (e.g., "Chart")
    title?: string; // Main title (e.g., "Unit Price")
    subtitle?: string; // Subtitle (e.g., "Price statistics for the last 31 days")
    height?: number;
    showLegend?: boolean;
    showDataZoom?: boolean;
    showToolbox?: boolean;
    xAxisType?: 'category' | 'time' | 'value';
    yAxisName?: string;
    xAxisName?: string;
    smooth?: boolean;
    areaStyle?: boolean;
    darkTheme?: boolean;
    isLoading?: boolean;
    mobileTimeRange?: TimeRangeOption; // Time range for mobile
    defaultTimeRange?: TimeRangeOption; // Default time range
    currencyUnit?: 'gold' | 'silver' | 'copper'; // Currency unit for formatting values
    grid?: {
        top?: number | string;
        right?: number | string;
        bottom?: number | string;
        left?: number | string;
    };
}

const props = withDefaults(defineProps<ChartProps>(), {
    height: 400,
    showLegend: true,
    showDataZoom: true,
    showToolbox: true,
    xAxisType: 'category',
    smooth: false,
    areaStyle: false,
    darkTheme: false,
    isLoading: false,
    mobileTimeRange: '1 day',
    defaultTimeRange: '7 days',
    grid: () => ({ top: 60, right: 40, bottom: 60, left: 60 })
});
const timeRangeToHours = (timeRange: TimeRangeOption): number => {
    switch (timeRange) {
        case '1 day':
            return 24;
        case '3 days':
            return 72;
        case '7 days':
            return 168;
        case '14 days':
            return 336;
        case '30 days':
            return 720;
        default:
            return 24;
    }
};

const emit = defineEmits<{
    chartClick: [params: any];
    legendChange: [params: any];
}>();
const loading = ref(false);
const error = ref<string | null>(null);
const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024);
const chartInstance = ref<any>(null);
const timeRangeDropdown = ref<HTMLDetailsElement | null>(null);

const isMobile = computed(() => windowWidth.value < 768);
const getInitialTimeRange = (): TimeRangeOption => {
    return isMobile.value ? props.mobileTimeRange : props.defaultTimeRange;
};

const selectedTimeRange = ref<TimeRangeOption>(getInitialTimeRange());
const hasData = computed(() => Array.isArray(props.data) && props.data.length > 0);
const getStartValue = () => {
    // Calculate start time for "last X days" ending at current time
    // This ensures we show the full time range even when data is limited
    // Add 1 hour of padding to provide buffer space
    const now = Date.now();
    const timeRangeHours = timeRangeToHours(selectedTimeRange.value);
    const paddingHours = 1; // Add 1 hour of padding
    const startTimestamp = now - (timeRangeHours + paddingHours) * 60 * 60 * 1000;

    return startTimestamp;
};

const responsiveHeight = computed(() => {
    const w = windowWidth.value;
    if (w < 480) return Math.max(300, props.height * 0.7);
    if (w < 768) return Math.max(350, props.height * 0.8);
    if (w < 1024) return Math.max(400, props.height * 0.9);
    return props.height;
});

const responsiveGrid = computed(() => {
    const w = windowWidth.value;
    if (w < 480) return { top: 30, right: 10, bottom: 70, left: 0 };
    if (w < 768) return { top: 40, right: 15, bottom: 80, left: 0 };
    return { top: 60, right: 20, bottom: 60, left: 0 };
});

const responsiveFontSize = computed(() => {
    const w = windowWidth.value;
    if (w < 480) return 10;
    if (w < 768) return 12;
    return 14;
});

const responsiveSymbolSize = computed(() => {
    const w = windowWidth.value;
    if (w < 480) return 3;
    if (w < 768) return 4;
    return 5;
});

const responsiveLineWidth = computed(() => {
    const w = windowWidth.value;
    if (w < 480) return 1.5;
    if (w < 768) return 1.8;
    return 2;
});

const lastHi = ref<{ seriesIndex: number; dataIndex: number } | null>(null);
const formatNumber = (value: number) => {
    if (value >= 1_000_000) return (value / 1_000_000).toFixed(1) + 'm';
    if (value >= 1_000) return (value / 1_000).toFixed(1) + 'k';
    return value.toString();
};

const chartOption = computed(() => {
    const colors = ['#64b5f6', '#81c784', '#ffb74d', '#e57373', '#4fc3f7', '#4db6ab', '#ff8a65', '#ba68c8', '#f06292'];

    if (!hasData.value) {
        return {
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(33,33,33,0.95)',
                borderColor: '#555',
                borderWidth: 1,
                textStyle: { color: '#c2c7d0' }
            },
            grid: { ...responsiveGrid.value, containLabel: true },
            xAxis: {
                type: props.xAxisType,
                name: props.xAxisName,
                nameLocation: 'center',
                nameGap: 30,
                nameTextStyle: { color: '#c2c7d0' },
                axisLine: { lineStyle: { color: '#555' } },
                axisTick: { lineStyle: { color: '#555' } },
                min: getStartValue(), // Ensure x-axis starts at the beginning of the time range
                max: Date.now(), // Ensure x-axis ends at current time
                axisLabel: { color: '#b0b0b0', fontSize: 10 }
            },
            yAxis: {
                type: 'value',
                name: props.yAxisName,
                nameLocation: 'middle',
                nameGap: 80,
                nameTextStyle: { color: '#c2c7d0' },
                axisLine: { lineStyle: { color: '#555' } },
                axisTick: { lineStyle: { color: '#555' } },
                axisLabel: { color: '#b0b0b0', fontSize: 10 },
                splitLine: { lineStyle: { color: '#424242', type: 'dashed' } }
            },
            series: []
        };
    }

    const series = props.data.map((item, i) => ({
        name: item.name,
        type: 'line',
        data: item.data,
        color: item.color || colors[i % colors.length],
        smooth: props.smooth,
        areaStyle: props.areaStyle ? { opacity: 0.1 } : undefined,
        lineStyle: { width: responsiveLineWidth.value },
        symbol: 'circle',
        symbolSize: responsiveSymbolSize.value,
        showSymbol: true,
        hoverAnimation: !isMobile.value,
        emphasis: {
            focus: 'none',
            scale: false,
            itemStyle: { borderWidth: 0, borderColor: 'transparent', shadowBlur: 0, shadowColor: 'transparent' }
        }
    }));

    return {
        animation: !isMobile.value,
        animationDuration: !isMobile.value ? 1000 : 0,
        animationEasing: !isMobile.value ? 'cubicOut' : 'linear',
        tooltip: {
            trigger: 'axis',
            triggerOn: 'mousemove|click',
            backgroundColor: 'rgba(24,28,37,0.95)',
            borderColor: '#555',
            borderWidth: 1,
            textStyle: { color: '#c2c7d0', fontSize: responsiveFontSize.value + 2, fontFamily: '"Open Sans", Arial, sans-serif' },
            axisPointer: {
                type: 'line',
                label: { show: false },
                lineStyle: { opacity: 0.7 }
            },
            confine: true,
            enterable: true,
            position: undefined,
            showDelay: 0,
            hideDelay: 0,
            formatter(params: any) {
                const ts = params[0].axisValue;
                let dateStr: string;
                if (typeof ts === 'number' && ts > 1_000_000_000_000) dateStr = new Date(ts).toLocaleString();
                else if (typeof ts === 'number') dateStr = new Date(ts * 1000).toLocaleString();
                else dateStr = ts;
                let out = dateStr + '<br/>';
                params.forEach((p: any) => {
                    const value = p.value[1];
                    const formattedValue = props.currencyUnit ? formatCurrencyForChart(value, props.currencyUnit) : formatNumber(value);
                    out += `${p.marker} ${p.seriesName}: ${formattedValue}<br/>`;
                });
                return out;
            }
        },
        legend: {
            show: props.showLegend,
            type: 'scroll',
            orient: 'horizontal',
            bottom: isMobile.value ? '10' : '0',
            textStyle: { fontSize: responsiveFontSize.value, color: '#ffffff', fontFamily: '"Open Sans", Arial, sans-serif' },
            pageButtonItemGap: isMobile.value ? 8 : 10,
            pageButtonGap: isMobile.value ? 8 : 10,
            pageButtonPosition: 'end',
            pageIconSize: isMobile.value ? 16 : 20,
            selected: props.data.reduce(
                (acc, item) => {
                    acc[item.name] = item.selected !== false;
                    return acc;
                },
                {} as Record<string, boolean>
            )
        },
        grid: { ...responsiveGrid.value, containLabel: true },
        xAxis: {
            type: props.xAxisType,
            name: props.xAxisName,
            nameLocation: 'center',
            nameGap: 30,
            nameTextStyle: { color: '#c2c7d0', fontFamily: '"Open Sans", Arial, sans-serif' },
            axisLine: { lineStyle: { color: '#555' } },
            axisTick: { lineStyle: { color: '#555' } },
            min: getStartValue(), // Ensure x-axis starts at the beginning of the time range
            max: Date.now(), // Ensure x-axis ends at current time
            axisLabel: {
                color: '#b0b0b0',
                fontSize: responsiveFontSize.value,
                fontFamily: '"Open Sans", Arial, sans-serif',
                interval: isMobile.value ? 'auto' : 0,
                rotate: isMobile.value ? 45 : 0,
                margin: isMobile.value ? 8 : 6,
                formatter(value: any) {
                    if (typeof value === 'number' && value > 1_000_000_000_000) {
                        const d = new Date(value);
                        const hh = d.getHours().toString().padStart(2, '0');
                        const mm = d.getMinutes().toString().padStart(2, '0');
                        const day = d.getDate();
                        const mon = d.toLocaleString('en', { month: 'short' });
                        return hh === '00' && mm === '00' ? `${mon} ${day}` : `${hh}:${mm}`;
                    }
                    return String(value);
                }
            }
        },
        yAxis: {
            type: 'value',
            name: props.yAxisName,
            nameLocation: 'middle',
            nameGap: 80,
            nameTextStyle: { color: '#c2c7d0', fontFamily: '"Open Sans", Arial, sans-serif' },
            axisLine: { lineStyle: { color: '#555' } },
            axisTick: { lineStyle: { color: '#555' } },
            axisLabel: {
                color: '#b0b0b0',
                fontSize: responsiveFontSize.value,
                fontFamily: '"Open Sans", Arial, sans-serif',
                margin: isMobile.value ? 12 : 16,
                formatter: (v: number) => (props.currencyUnit ? formatCurrencyForChart(v, props.currencyUnit) : formatNumber(v))
            },
            splitLine: { lineStyle: { color: '#424242', type: 'dashed' } }
        },
        dataZoom: props.showDataZoom
            ? [
                  {
                      type: 'inside',
                      startValue: getStartValue(),
                      endValue: Date.now(), // Always end at current time to show full range
                      zoomOnMouseWheel: false,
                      moveOnMouseMove: true,
                      zoomOnPinch: false,
                      moveOnPinch: true,
                      preventDefaultMouseMove: isMobile.value,
                      throttle: isMobile.value ? 70 : 100,
                      rangeMode: ['value', 'value']
                  }
              ]
            : [],
        toolbox: props.showToolbox
            ? {
                  feature: { restore: {}, saveAsImage: {} },
                  right: isMobile.value ? 10 : 20,
                  top: isMobile.value ? 10 : 20,
                  itemSize: isMobile.value ? 20 : 24,
                  itemGap: isMobile.value ? 10 : 12
              }
            : undefined,
        series
    };
});

const handleChartClick = (params: any) => {
    const chart = chartInstance.value?.chart;
    if (!chart) return;

    if (!isMobile.value) {
        emit('chartClick', params);
        return;
    }
    const { seriesIndex, dataIndex } = params ?? {};
    if (seriesIndex == null || dataIndex == null) return;

    const same = lastHi.value && lastHi.value.seriesIndex === seriesIndex && lastHi.value.dataIndex === dataIndex;

    if (lastHi.value) chart.dispatchAction({ type: 'downplay', ...lastHi.value });
    chart.dispatchAction({ type: 'hideTip' });

    if (!same) {
        chart.dispatchAction({ type: 'highlight', seriesIndex, dataIndex });
        chart.dispatchAction({ type: 'showTip', seriesIndex, dataIndex });
        lastHi.value = { seriesIndex, dataIndex };
    } else {
        lastHi.value = null;
    }

    emit('chartClick', params);
};

const handleLegendChange = (params: any) => emit('legendChange', params);

const selectTimeRange = (timeRange: TimeRangeOption) => {
    selectedTimeRange.value = timeRange;
    if (timeRangeDropdown.value) {
        timeRangeDropdown.value.open = false;
    }

    // Re-trigger animation by updating chart option
    nextTick(() => {
        const chart = chartInstance.value?.chart;
        if (chart && !isMobile.value) {
            // Force re-render with animation
            chart.setOption(chartOption.value, true);

            // Re-enable emphasis effects after animation completes
            setTimeout(() => {
                const seriesUpdates = props.data.map((item, i) => ({
                    emphasis: {
                        focus: 'none',
                        scale: true,
                        itemStyle: { borderWidth: 2, borderColor: '#fff', shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' }
                    }
                }));

                chart.setOption(
                    {
                        series: seriesUpdates
                    },
                    false
                );
            }, 1000); // Wait for animation to complete
        }
    });
};
const handleResize = () => {
    windowWidth.value = window.innerWidth;
    setTimeout(() => {
        const c = chartInstance.value?.chart;
        if (!c) return;
        c.resize();
        if (isMobile.value && lastHi.value) {
            c.dispatchAction({ type: 'downplay', ...lastHi.value });
            c.dispatchAction({ type: 'hideTip' });
            lastHi.value = null;
        }
    }, 100);
};

onMounted(async () => {
    try {
        loading.value = true;
        error.value = null;

        window.addEventListener('resize', handleResize);

        await nextTick();
        await new Promise((r) => setTimeout(r, 100));

        const chart = chartInstance.value?.chart;
        if (chart) {
            chart.getZr().configLayer(0, { devicePixelRatio: window.devicePixelRatio || 1 });

            chart.setOption({ textStyle: { fontFamily: '"Open Sans", Arial, sans-serif', fontSize: responsiveFontSize.value } }, true);
            chart.getZr().on('globalout', () => {
                if (!isMobile.value) return;
                if (lastHi.value) chart.dispatchAction({ type: 'downplay', ...lastHi.value });
                chart.dispatchAction({ type: 'hideTip' });
                lastHi.value = null;
            });

            chart.on('dataZoom', () => {
                if (!isMobile.value) return;
                if (lastHi.value) chart.dispatchAction({ type: 'downplay', ...lastHi.value });
                chart.dispatchAction({ type: 'hideTip' });
                lastHi.value = null;
            });
        }

        loading.value = false;
    } catch (e: any) {
        error.value = e?.message ?? 'Failed to load chart';
        loading.value = false;
    }
});

onUnmounted(() => {
    window.removeEventListener('resize', handleResize);
});

watch(
    () => props.data,
    () => {},
    { deep: true }
);

watch(selectedTimeRange, () => {});

watch(responsiveHeight, () => {
    setTimeout(() => chartInstance.value?.chart?.resize(), 50);
});
watch(isMobile, (newIsMobile) => {
    const appropriateTimeRange = newIsMobile ? props.mobileTimeRange : props.defaultTimeRange;
    selectedTimeRange.value = appropriateTimeRange;
});
</script>

<style scoped>
.chart-container {
    width: 100%;
    position: relative;
    padding: 0;
}

.chart-content {
    position: relative;
}

.header-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
}

hgroup {
    flex: 1;
    margin-bottom: 0;
}

.chart-controls {
    flex-shrink: 0;
    min-width: 125px;
}

.time-range-dropdown {
    min-width: 125px;
}

.time-range-dropdown summary:hover,
.time-range-dropdown summary:focus {
    border-color: var(--pico-muted-border-color) !important;
    box-shadow: none !important;
    background-color: var(--pico-form-element-background-color) !important;
}

.time-range-dropdown summary {
    border-color: var(--pico-muted-border-color) !important;
    box-shadow: none !important;
}

.chart-wrapper {
    width: 100%;
    border-radius: 8px;
    overflow: hidden;
    margin: 0;
    padding: 0;
    position: relative;
}

.loading {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    color: #c2c7d0;
    font-size: 14px;
    text-align: center;
}

.error {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: #e74c3c;
    font-size: 14px;
    text-align: center;
    padding: 20px;
}

hgroup {
    margin-bottom: 0;
}

.no-data {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: #c2c7d0;
    font-size: 14px;
    text-align: center;
    padding: 20px;
    background: transparent;
    border: 1px dashed #555;
    border-radius: 8px;
}

:deep(.echarts) {
    width: 100% !important;
    height: 100% !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
}

@media (hover: none) and (pointer: coarse) {
    .chart-wrapper {
        -webkit-tap-highlight-color: transparent;
        touch-action: pan-x pan-y pinch-zoom;
    }

    .chart-container {
        -webkit-tap-highlight-color: transparent;
    }
}

@media (max-width: 480px) {
    .chart-container {
        padding: 0;
        margin: 0;
        width: 100%;
    }

    .header-section {
        flex-direction: column;
        align-items: stretch;
        gap: 0.5rem;
    }

    .chart-controls {
        width: 100%;
    }

    .time-range-dropdown summary {
        font-size: 0.8rem;
        padding: 0.4rem 0.6rem;
    }

    .chart-wrapper {
        border-radius: 4px;
    }

    .loading,
    .error,
    .no-data {
        height: 120px;
        font-size: 12px;
    }
}

@media (min-width: 481px) and (max-width: 768px) {
    .chart-container {
        padding: 0 0.25rem;
        width: 100%;
    }

    .loading,
    .error,
    .no-data {
        height: 150px;
        font-size: 13px;
    }
}
</style>
