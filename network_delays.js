import http from 'k6/http';
import { sleep, check } from 'k6';

// Retrieve the microservice URL from environment variables
const BASE_URL = __ENV.MICROSERVICE_URL || 'http://default-microservice-url/';

export let options = {
    stages: [
        { duration: '1m', target: 5 }, // ramp up to 5 users
        { duration: '2m', target: 5 }, // stay at 5 users
        { duration: '1m', target: 0 }, // ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<2000'], // 95% of requests must complete below 2 seconds
    },
};

export default function () {
    let response = http.get(`${BASE_URL}`, {
        tags: {name: 'NetworkDelay'},
        timeout: '10s',  // Set high timeout in case of delays
    });
    check(response, {
        'is status 200': (r) => r.status === 200,
    });
    sleep(1);
}
