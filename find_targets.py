import requests
import time
import json
import os  # 환경 변수를 읽어오기 위한 라이브러리

# 깃허브 시크릿(금고)에서만 키를 가져옵니다. 
# 이제 코드 내부에는 그 어떤 키 문자열도 남아있지 않습니다.
API_KEY = os.environ.get("STEAM_API_KEY")

def get_target_games():
    # 만약 환경 변수에 키가 세팅되지 않았다면 에러를 내고 안전하게 종료합니다.
    if not API_KEY:
        print("[!] 에러: STEAM_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("[!] 깃허브 Settings -> Secrets에 키를 올바르게 등록했는지 확인하세요.")
        return

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
            # 상세 정보 API 호출
            detail_url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
            data = requests.get(detail_url).json()
            
            if data and data[str(appid)]['success']:
                app_data = data[str(appid)]['data']
                name = app_data.get('name')
                categories = [c['description'] for c in app_data.get('categories', [])]
                
                # 멀티플레이 관련 키워드 필터링
                target_keywords = ['Multi-player', 'Online Co-op', 'P2P', 'Co-op', 'Lobby']
                if any(kw in categories for kw in target_keywords):
                    final_targets.append({"appid": appid, "name": name})
                    print(f"   [+] 타겟 발견: {name} ({appid})")
            
            time.sleep(1) # 디도스 오인 방지 지연시간
            
        except Exception as e:
            print(f"   [!] {appid} 처리 중 에러: {e}")
            continue

    # 결과를 targets.json 파일로 저장
    with open('targets.json', 'w', encoding='utf-8') as f:
        json.dump(final_targets, f, ensure_ascii=False, indent=4)
    
    print(f"\n모든 작업 완료! 총 {len(final_targets)}개의 게임이 targets.json에 저장되었습니다.")

if __name__ == "__main__":
    get_target_games()