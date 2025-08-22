import { defineConfig } from '@rsbuild/core';
import { pluginVue } from '@rsbuild/plugin-vue';

const LOT_HOSTNAME = process.env.PUBLIC_LOT_HOST || 'http://localhost:8007/';
const ANALYTICS_CODE = process.env.PUBLIC_ANALYTICS_CODE || '';
const IS_PROD = process.env.NODE_ENV === 'production';

export default defineConfig({
    plugins: [pluginVue()],
    source: {
        entry: {
            index: './src/index.ts'
        },
        define: {
            'process.env.PUBLIC_LOT_HOST': JSON.stringify(LOT_HOSTNAME),
            'process.env.PUBLIC_ANALYTICS_CODE': JSON.stringify(ANALYTICS_CODE)
        }
    },
    html: {
        template: './index.html',
        templateParameters: {
            PUBLIC_ANALYTICS_CODE: ANALYTICS_CODE
        }
    },
    server: {
        host: '0.0.0.0',
        port: 5173
    },
    output: {
        minify: IS_PROD,
        sourceMap: !IS_PROD,
        filename: {
            css: IS_PROD ? 'assets/[name].[contenthash:8].css' : 'assets/[name].css',
            js: IS_PROD ? 'assets/[name].[contenthash:8].js' : 'assets/[name].js'
        }
    }
});
