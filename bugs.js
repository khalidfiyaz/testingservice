import http from 'k6/http';
import { check } from 'k6';

// Retrieve the microservice URL from environment variables
const BASE_URL = __ENV.MICROSERVICE_URL || 'http://default-microservice-url/';

export default function () {
    let payloads = [
        {"data": "unexpected_string"},
        {"data": ""},
        {"data": {"nested": "object"}},
    ];

    payloads.forEach(payload => {
        let res = http.post(`${BASE_URL}/buggy-endpoint`, JSON.stringify(payload), {
            headers: { 'Content-Type': 'application/json' },
        });
        check(res, {'status was 200': (r) => r.status === 200});
    });
}
