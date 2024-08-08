import http from 'k6/http';
import { sleep, check } from 'k6';

const BASE_URL = __ENV.MICROSERVICE_URL || 'http://default-microservice-url/';

export let options = {
    stages: [
        { duration: '1m', target: 5 },
        { duration: '2m', target: 5 },
        { duration: '1m', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(95)<2000'],
    },
};

export default function () {
    let response = http.get(`${BASE_URL}`, {
        tags: { name: 'NetworkDelay' },
        timeout: '10s',
    });
    check(response, {
        'is status 200': (r) => r.status === 200,
        'body is not empty': (r) => r.body.length > 0,
    });
    console.log(`Request duration for ${response.url}: ${response.timings.duration} ms`);
    sleep(1);
}
