const request = require('supertest');
const app = require('../app'); // Import your Express app

describe('GET / for test-nodejs-app_1', () => {
  it('should respond with Hello message', async () => {
    const res = await request(app).get('/');
    expect(res.statusCode).toEqual(200);
    expect(res.text).toBe('Hello from Microservice B (Node.js/Express)!');
  });
});

describe('GET /health for test-nodejs-app_1', () => {
  it('should respond with health status', async () => {
    const res = await request(app).get('/health');
    expect(res.statusCode).toEqual(200);
    expect(res.body).toEqual({ status: 'UP', service: 'test-nodejs-app_1' });
  });
});