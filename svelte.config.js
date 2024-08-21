import adapter from '@sveltejs/adapter-auto';
import sveltePreprocess from 'svelte-preprocess';

export default {
  kit: {
    adapter: adapter(),
  },
  preprocess: sveltePreprocess(),
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        pathRewrite: { '^/api': '' },
      },
    },
  },
};