import http from 'k6/http';
import { sleep, check } from 'k6';
import disruptor from 'k6/x/disruptor';

export let options = {
    vus: 1,
    iterations: 1,
};

export default function () {
    // Introduce a fault in the 'booking' microservice
    disruptor.shutdown({
        target: 'booking', // Target the 'booking' microservice for disruption
        duration: '10s', // Duration for the shutdown
    });

    // Wait for the effect of the shutdown to manifest
    sleep(10);

    // After shutdown, check the status of other microservices
    const services = [
        "http://identity:6005/api/status", // Check identity service
        "http://gateway:5001/api/status",  // Check gateway service
        "http://flight:5004/api/status"    // Check flight service
    ];

    services.forEach(url => {
        let response = http.get(url);
        check(response, {
            'status is 200': r => r.status === 200,
            'response time is acceptable': r => r.timings.duration < 1000
        });
    });
}
