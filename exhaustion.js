import http from 'k6/http';
import { sleep } from 'k6';

// Retrieve the microservice URL from environment variables
const BASE_URL = __ENV.MICROSERVICE_URL || 'http://default-microservice-url/';

export let options = {
    stages: [
        { duration: '2m', target: 100 }, // ramp up to 100 users
        { duration: '3m', target: 100 }, // hold at 100 users
        { duration: '2m', target: 0 },   // ramp down to 0 users
    ],
};

export default function () {
    http.get(`${BASE_URL}`);
    sleep(1);
}
