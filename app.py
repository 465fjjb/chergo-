import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Функция для безопасной загрузки JSON
def load_json_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return []

# Инициализация файлов
places_data = load_json_file('places.json')
load_json_file('favorites.json')
load_json_file('routes.json')

@app.route('/')
def index():
    return render_template('index.html', places=places_data)

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    category = request.args.get('category', 'all')
    
    filtered_places = []
    for place in places_data:
        name_match = query in place.get('name', '').lower()
        desc_match = query in place.get('description', '').lower()
        category_match = (category == 'all') or (place.get('category') == category)
        
        if (name_match or desc_match or not query) and category_match:
            filtered_places.append(place)
    
    return render_template('search.html', places=filtered_places, query=query, category=category)

@app.route('/place/<int:place_id>')
def place(place_id):
    place = next((p for p in places_data if p['id'] == place_id), None)
    if not place:
        return "Место не найдено", 404
    
    favorites = load_json_file('favorites.json')
    is_favorite = any(fav['id'] == place_id for fav in favorites)
    
    return render_template('place.html', place=place, is_favorite=is_favorite)

@app.route('/route')
def route():
    place_ids = [int(id) for id in request.args.get('places', '').split(',') if id]
    route_places = [p for p in places_data if p['id'] in place_ids]
    route_name = request.args.get('name', 'Мой маршрут')
    return render_template('route.html', places=route_places, route_name=route_name)

@app.route('/saved-routes')
def saved_routes():
    saved_routes = load_json_file('routes.json')
    for route in saved_routes:
        route['places'] = [p for p in places_data if p['id'] in route['place_ids']]
    return render_template('saved_routes.html', routes=saved_routes)

@app.route('/favorites')
def favorites():
    favorites = load_json_file('favorites.json')
    favorite_places = []
    for fav in favorites:
        place = next((p for p in places_data if p['id'] == fav['id']), None)
        if place:
            place['note'] = fav.get('note', '')
            favorite_places.append(place)
    return render_template('favorites.html', places=favorite_places)

@app.route('/api/toggle_favorite', methods=['POST'])
def toggle_favorite():
    data = request.get_json()
    place_id = data.get('place_id')
    
    favorites = load_json_file('favorites.json')
    index = next((i for i, fav in enumerate(favorites) if fav['id'] == place_id), -1)
    
    if index >= 0:
        favorites.pop(index)
        action = 'removed'
    else:
        favorites.append({'id': place_id})
        action = 'added'
    
    with open('favorites.json', 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False)
    
    return jsonify({'status': 'success', 'action': action})

@app.route('/api/save_route', methods=['POST'])
def save_route():
    data = request.get_json()
    routes = load_json_file('routes.json')
    routes.append({
        'id': len(routes) + 1,
        'name': data.get('name', 'Мой маршрут'),
        'place_ids': data.get('place_ids', [])
    })
    
    with open('routes.json', 'w', encoding='utf-8') as f:
        json.dump(routes, f, ensure_ascii=False)
    
    return jsonify({'status': 'success'})

@app.route('/api/delete_route', methods=['POST'])
def delete_route():
    data = request.get_json()
    routes = [r for r in load_json_file('routes.json') if r['id'] != data.get('route_id')]
    
    with open('routes.json', 'w', encoding='utf-8') as f:
        json.dump(routes, f, ensure_ascii=False)
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Важно: host='0.0.0.0'!