import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
    stages: [
        { duration: '30s', target: 100 },
        { duration: '1m', target: 300 },
    ],
};

const BASE_URL = 'http://localhost:8000/api/v1';

const TOKEN = 'USER_TOKEN';

export default function () {
    const headers = {
        'Authorization': `Bearer ${TOKEN}`,
        'Content-Type': 'application/json',
    };

    let resLots = http.get(`${BASE_URL}/lots/`, { headers: headers });
    check(resLots, { 'GET /lots success': (r) => r.status === 200 });

    let lotId = Math.floor(Math.random() * 10) + 1;
    let resSpots = http.get(`${BASE_URL}/lots/${lotId}/spots/`, { headers: headers });
    check(resSpots, { 'GET /spots success': (r) => r.status === 200 });

    let spotId = Math.floor(Math.random() * 1000) + 1;
    
    let startAt = new Date();
    startAt.setDate(startAt.getDate() + Math.floor(Math.random() * 10) + 1);
    let endAt = new Date(startAt.getTime() + (Math.floor(Math.random() * 3) + 1) * 60 * 60 * 1000);

    let payload = JSON.stringify({
        spot: spotId,
        start_at: startAt.toISOString(),
        end_at: endAt.toISOString()
    });

    let resPost = http.post(`${BASE_URL}/bookings/create/`, payload, { headers: headers });
    
    check(resPost, {
        'POST /bookings success or validation': (r) => r.status === 201 || r.status === 409,
        'Database NOT locked (No 500)': (r) => r.status !== 500 && r.status !== 503,
    });

    sleep(Math.random() * 1 + 0.5); 
}