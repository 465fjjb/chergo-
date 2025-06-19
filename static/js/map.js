function initMap(places) {
    const map = L.map('map').setView([59.1266, 37.9094], 13);
    
    const baseLayers = {
        "Стандартная": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap'
        }),
        "Спутник": L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Tiles &copy; Esri'
        })
    };
    
    baseLayers["Стандартная"].addTo(map);
    L.control.layers(baseLayers).addTo(map);
    
    places.forEach(place => {
        L.marker([place.coordinates.lat, place.coordinates.lng])
            .addTo(map)
            .bindPopup(`<b>${place.name}</b><br><a href="/place/${place.id}">Подробнее</a>`);
    });
    
    locateUser(map);
}

function initPlaceMap(lat, lng, title) {
    const map = L.map('place-map').setView([lat, lng], 15);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    
    L.marker([lat, lng])
        .addTo(map)
        .bindPopup(`<b>${title}</b>`)
        .openPopup();
    
    return map;
}

function initRouteMap(places) {
    if (!places.length) return;
    
    const map = L.map('route-map');
    const coords = places.map(p => [p.coordinates.lat, p.coordinates.lng]);
    const bounds = L.latLngBounds(coords);
    map.fitBounds(bounds);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    
    if (places.length > 1) {
        L.polyline(coords, {color: 'blue'}).addTo(map);
    }
    
    places.forEach((place, idx) => {
        L.marker([place.coordinates.lat, place.coordinates.lng])
            .addTo(map)
            .bindPopup(`${idx+1}. ${place.name}`);
    });
    
    locateUser(map);
}

function locateUser(map) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(pos => {
            const userPos = [pos.coords.latitude, pos.coords.longitude];
            L.marker(userPos)
                .addTo(map)
                .bindPopup("Вы здесь")
                .openPopup();
            map.setView(userPos, 15);
        }, null, {enableHighAccuracy: true});
    }
}