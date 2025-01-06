const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.get('/health', (req, res) => {
    res.status(200).json({ 
        status: 'healthy',
        timestamp: new Date().toISOString()
    });
});

const server = app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});

process.on('SIGTERM', () => {
    server.close(() => {
        console.log('Server stopped');
        process.exit(0);
    });
});
