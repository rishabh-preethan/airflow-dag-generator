import express from 'express';
import cors from 'cors';
import { createProxyMiddleware } from 'http-proxy-middleware';

const app = express();

const corsOptions = {
    origin: 'http://localhost:5173',
    credentials: true,
    optionSuccessStatus: 200,
};

app.use(cors(corsOptions));
app.use(express.json());

// Proxy requests from the frontend to the backend
app.use('/api', createProxyMiddleware({
    target: 'http://localhost:5000',
    changeOrigin: true,
    pathRewrite: {
        '^/api': '', // Removes `/api` prefix when forwarding to the backend
    },
}));

app.listen(3000, () => {
    console.log('Proxy server running on http://localhost:3000');
});
