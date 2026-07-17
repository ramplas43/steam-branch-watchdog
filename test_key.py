import requests
import os

# 1. 환경 변수에서 키 가져오기
API_KEY = os.environ.get("STEAM_API_KEY")

def test_api_key():
    if not API_KEY:
        print("[!] 에러: 키가 환경 변수에 설정되지 않았습니다.")
        return

    # 스팀 API 목록을 가져오는 엔드포인트 (키가 정상이어야만 응답함)
    url = f"https://api.steampowered.com/ISteamWebAPIUtil/GetSupportedAPIList/v1/?key={API_KEY}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        print(f"[OK] API 키가 유효합니다! (응답 코드: 200)")
        # 응답 내용 중 일부 출력
        print(f"목록 일부: {response.text[:100]}...")
    elif response.status_code == 403:
        print(f"[FAIL] 403 Forbidden: 키가 잘못되었거나 만료되었습니다.")
    else:
        print(f"[FAIL] 에러 발생 (코드 {response.status_code}): {response.text}")

if __name__ == "__main__":
    test_api_key()
