import requests
import time
import json

# 여기에 본인의 API 키를 입력하세요
API_KEY = "0BB0BCA48D2D46E7BC80A778F5056061"

def get_target_games():
    print("1. 현재 동접자 상위 게임 목록 가져오는 중...")
    chart_url = f"https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/?key={API_KEY}"
    res = requests.get(chart_url).json()
    ranks = res.get('response', {}).get('ranks', [])
    
    # 5,000명 이상인 게임만 1차 필터링
    candidates = [g['appid'] for g in ranks if g.get('last_week_peak', 0) >= 5000]
    print(f"-> 5,000명 이상 후보군 {len(candidates)}개 발견.")

    final_targets = []
    
    print("2. 멀티플레이/P2P 태그 확인 중 (이 작업은 시간이 좀 걸립니다)...")
    for appid in candidates:
        try:
            # API 키 없이 상세 정보를 가져오는 공개 엔드포인트 사용 (IP 차단 방지 위해 천천히)
            detail_url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
            data = requests.get(detail_url).json()
            
            if data and data[str(appid)]['success']:
                app_data = data[str(appid)]['data']
                name = app_data.get('name')
                # 카테고리 정보 추출
                categories = [c['description'] for c in app_data.get('categories', [])]
                
                # 사용자가 요청한 키워드 필터링 (멀티플레이, P2P, Co-op 등)
                target_keywords = ['Multi-player', 'Online Co-op', 'P2P', 'Co-op', 'Lobby']
                if any(kw in categories for kw in target_keywords):
                    final_targets.append({"appid": appid, "name": name})
                    print(f"   [+] 타겟 발견: {name} ({appid})")
            
            # 스팀 서버 차단을 피하기 위한 1초 휴식
            time.sleep(1)
            
        except Exception as e:
            print(f"   [!] {appid} 처리 중 에러: {e}")
            continue

    # 결과를 targets.json 파일로 저장
    with open('targets.json', 'w', encoding='utf-8') as f:
        json.dump(final_targets, f, ensure_ascii=False, indent=4)
    
    print(f"\n모든 작업 완료! 총 {len(final_targets)}개의 게임이 targets.json에 저장되었습니다.")

if __name__ == "__main__":
    get_target_games()
