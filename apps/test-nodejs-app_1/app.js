const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.send('Hello from Microservice B (Node.js/Express)!');
});

app.get('/health', (req, res) => {
  res.status(200).json({ status: 'UP', service: 'test-nodejs-app_1' });
});

// Only start listening if not in test environment
if (process.env.NODE_ENV !== 'test') {
  app.listen(port, () => {
    console.log(`test-nodejs-app_1 listening at http://localhost:${port}`);
  });
}

module.exports = app; // Export for testing