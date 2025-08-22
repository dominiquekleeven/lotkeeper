<template>
    <main class="container">
        <DynamicContent>
            <h1>404 - Page Not Found</h1>
            <p>The page you are looking for does not exist.</p>
            <router-link to="/">Go back to the main page</router-link>
        </DynamicContent>
    </main>
</template>

<script setup lang="ts">
import DynamicContent from '../components/DynamicContent.vue';
</script>

<style scoped>
.container {
    text-align: center;
}
</style>
