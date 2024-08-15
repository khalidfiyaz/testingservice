import http from 'k6/http';
import { check, sleep } from 'k6';

// Retrieve the microservice URL from environment variables
const BASE_URL = __ENV.MICROSERVICE_URL || 'http://cloned_microservice:5001';

export let options = {
    vus: 10, // Number of virtual users
    duration: '30s', // Duration of the test
};

export default function () {
    let response = http.get(`${BASE_URL}`);
    check(response, {
        'is status 200': r => r.status === 200,
    });
    sleep(1);
}
