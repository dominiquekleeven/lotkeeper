<template>
    <img
        class="icon-border"
        :src="iconUrl"
        :alt="alt"
        :style="iconStyle"
        crossorigin="anonymous"
        onerror="this.onerror=null; this.src='/icons/inv_misc_questionmark.jpg'" />
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { getIconUrl } from '../common/util';

interface Props {
    icon: string;
    alt?: string;
    size?: number;
    width?: number;
    height?: number;
}

const props = withDefaults(defineProps<Props>(), {
    alt: 'ico',
    size: 32
});

const iconUrl = computed(() => getIconUrl(props.icon));

const iconStyle = computed(() => {
    if (props.width && props.height) {
        return `width: ${props.width}px; height: ${props.height}px`;
    }
    return `width: ${props.size}px; height: ${props.size}px`;
});
</script>
