import requests
import json
import time

def fetch_jamendo_tracks(client_id, limit=200, offset=0):
    """Получение треков с пагинацией (максимум 200 за запрос)"""
    url = "https://api.jamendo.com/v3.0/tracks/"
    params = {
        'client_id': client_id,
        'format': 'json',
        'limit': min(limit, 200),  
        'offset': offset,
        'include': 'musicinfo',
        'audioformat': 'mp32'
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data['headers']['status'] == 'success':
        return data['results']
    else:
        print(f"  Error: {data['headers']['error_message']}")
        return []

def fetch_all_tracks(client_id, total_needed=1000):
    """Получение нужного количества треков через несколько запросов"""
    all_tracks = []
    offset = 0
    batch_size = 200
    
    while len(all_tracks) < total_needed:
        print(f"Загружаем треки с offset={offset}...")
        batch = fetch_jamendo_tracks(client_id, limit=batch_size, offset=offset)
        
        if not batch:
            print("Больше треков нет")
            break
        
        all_tracks.extend(batch)
        print(f"  Загружено {len(batch)} треков. Всего: {len(all_tracks)}/{total_needed}")
        
        offset += batch_size
        time.sleep(0.5)  
    
    return all_tracks[:total_needed]


CLIENT_ID = "4359b26e"


print("Начинаем загрузку треков...")
tracks = fetch_all_tracks(CLIENT_ID, total_needed=1000)

print(f"\n{'='*80}")
print(f"ВСЕГО ПОЛУЧЕНО ТРЕКОВ: {len(tracks)}")
print(f"{'='*80}\n")


for idx, track in enumerate(tracks[:10], 1):
    print(f"🎵 ТРЕК #{idx}")
    print(f"{'─'*50}")
    print(f"  Название: {track.get('name', 'N/A')}")
    print(f"  Артист: {track.get('artist_name', 'N/A')}")
    print(f"  Длительность: {track.get('duration', 'N/A')} сек")
    print(f"  Жанр: {track.get('genre', 'N/A')}")
    print(f"  Прямая ссылка MP3: {track.get('audio', 'N/A')[:80]}...")
    print(f"{'─'*50}\n")

print(f"... и еще {len(tracks) - 10} треков")


with open('jamendo_tracks_1000.json', 'w', encoding='utf-8') as f:
    json.dump(tracks, f, indent=2, ensure_ascii=False)
print(f"\n💾 Полные данные сохранены в файл: jamendo_tracks_1000.json")