import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import WindiCSS from "vite-plugin-windicss";
import AutoImport from "unplugin-auto-import/vite";
import Components from "unplugin-vue-components/vite";
import { ElementPlusResolver } from "unplugin-vue-components/resolvers";

// https://vitejs.dev/config/
export default defineConfig({
  base: "/xiaoxiang/csust/",
  plugins: [
    vue(),
    WindiCSS(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  build: {
    chunkSizeWarningLimit: 2000, // 设置更高的值
  },
  server: {
    host: "0.0.0.0",
    // port: 8080,
    proxy: {
      "/auth-api": {
        target: "http://127.0.0.1:8001",
        // target: "http://192.168.4.117:8001",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/auth-api/, ""),
      },
      "/data-api": {
        target: "http://127.0.0.1:8002",
        // target: "http://192.168.4.117:8002",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/data-api/, ""),
      },
      "/single-model-api": {
        target: "http://127.0.0.1:48011",
        // target: "http://192.168.4.117:48011",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/single-model-api/, ""),
      },
      "/expert-model-api": {
        target: "http://127.0.0.1:48012",
        // target: "http://192.168.4.117:48012",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/expert-model-api/, ""),
      },
      "/test-model-api": {
        target: "http://127.0.0.1:48021",
        // target: "http://192.168.4.117:48021",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/test-model-api/, ""),
      },
      "/minio-api": {
        target: "http://127.0.0.1:9000",
        // target: "http://192.168.4.117:9000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/minio-api/, ""),
      },
    },
  },
});
