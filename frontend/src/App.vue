<template>
    <div class="app">
        <!-- Navbar -->
        <Navbar />

        <!-- Main Content -->
        <main class="container" id="app">
            <router-view />

            <!-- Footer -->
            <footer>
                <div class="footer-content">
                    <!-- Navigation Links -->
                    <div class="footer-nav">
                        <router-link to="/" class="footer-link">Home</router-link>
                        <router-link to="/faq" class="footer-link">FAQ</router-link>
                        <router-link to="/docs" class="footer-link">Docs</router-link>
                        <router-link to="/disclaimer" class="footer-link">Privacy Policy</router-link>
                        <router-link to="/disclaimer" class="footer-link">Legal & Disclaimer</router-link>
                    </div>

                    <!-- Social Media Icons -->
                    <div class="footer-social">
                        <a href="https://ko-fi.com/lotkeeper" target="_blank"
                            ><img src="/images/kofi.png" alt="Ko-fi" class="social-link"
                        /></a>
                        <a href="https://www.wtfast.com?fpr=lotkeeper&fp_sid=web" target="_blank"
                            ><img src="/images/wtfast.webp" alt="WTfast" class="social-link"
                        /></a>
                    </div>

                    <!-- Copyright -->
                    <div class="footer-copyright">
                        <span>&copy; 2025 Lotkeeper - All rights reserved</span>
                    </div>
                </div>
            </footer>
        </main>
    </div>
</template>

<script setup lang="ts">
import Navbar from './components/Navbar.vue';
</script>

<style>
main {
    min-height: calc(100vh - 425px);
    padding-top: 6.5rem;
}

main .container {
    padding-top: 0 !important;
}

footer {
    margin-top: auto;
    padding: 2rem 0;
    background: var(--pico-background-color);
    border-top: 1px solid var(--pico-muted-border-color);
}

.footer-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

.footer-nav {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}

.footer-link {
    color: var(--pico-muted-color);
    text-decoration: none;
    font-size: 0.9rem;
    transition: color 0.2s ease;
}

.footer-link:hover {
    color: var(--pico-primary);
}

.footer-social {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}

.social-link {
    color: var(--pico-muted-color);
    text-decoration: none;
    font-size: 1.5rem;
    transition: color 0.2s ease;
    max-width: 6rem;
    height: auto;
    transition: 0.3s ease-in-out;
    opacity: 0.80;
}

.social-link:hover {
    color: var(--pico-primary);
    opacity: 1;
    cursor: pointer;
}

.footer-copyright {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    color: var(--pico-muted-color);
    font-size: 0.9rem;
}

.footer-logo {
    max-width: 24px;
    height: auto;
    transition: transform 0.2s ease;
}

.footer-logo:hover {
    transform: scale(1.1);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    .footer-nav {
        gap: 1rem;
    }

    .footer-link {
        font-size: 0.8rem;
    }

    .footer-copyright {
        flex-direction: column;
        gap: 0.5rem;
    }
}
</style>
