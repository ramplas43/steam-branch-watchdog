import requests
import json
import os
import re
from discord_webhook import DiscordWebhook, DiscordEmbed

# 환경 변수 및 설정
API_KEY = os.environ.get("STEAM_API_KEY")
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
STATE_FILE = "last_state.json"
TARGET_FILE = "targets.json"

# 브랜치 감시용 정규식 (beta, staging, dev, test 등 포함)
BRANCH_REGEX = r".*(beta|staging|dev|test|internal|qa|debug).*"

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def check_updates():
    targets = load_json(TARGET_FILE) # [{"appid": 123, "name": "Game"}, ...]
    last_state = load_json(STATE_FILE) # {"appid": "last_chg_number"}
    
    if not targets:
        print("[!] targets.json이 비어있습니다. 먼저 find_targets를 실행하세요.")
        return

    new_state = last_state.copy()
    
    for game in targets:
        appid = str(game['appid'])
        name = game['name']
        
        # 1. 게임의 현재 Changelist 번호 확인
        # ISteamApps/GetAppBetas API를 사용하거나 
        # 간단하게 ISteamNews 등을 활용할 수 있지만, 가장 정확한 것은 AppInfo입니다.
        # 여기서는 웹 API 중 업데이트 상태를 볼 수 있는 엔드포인트를 활용합니다.
        url = f"https://api.steampowered.com/ISteamApps/GetAppBetas/v1/?key={API_KEY}&appid={appid}"
        
        try:
            res = requests.get(url).json()
            betas = res.get('response', {}).get('betas', {})
            
            if not betas:
                continue

            for branch_name, branch_info in betas.items():
                # 2. 브랜치 이름이 감시 대상(beta, staging 등)인지 정규식 검사
                if re.match(BRANCH_REGEX, branch_name, re.IGNORECASE):
                    last_buildid = branch_info.get('buildid')
                    state_key = f"{appid}_{branch_name}"
                    
                    # 3. 이전에 확인한 buildid와 다른 경우 (새로운 업데이트 발생!)
                    if str(last_buildid) != str(last_state.get(state_key)):
                        print(f"[*] 업데이트 감지! {name} - {branch_name}")
                        send_discord_alert(name, appid, branch_name, last_buildid)
                        new_state[state_key] = last_buildid

        except Exception as e:
            print(f"[!] {name}({appid}) 확인 중 에러: {e}")
            continue
        
    save_json(STATE_FILE, new_state)

def send_discord_alert(name, appid, branch, buildid):
    if not WEBHOOK_URL:
        return
        
    webhook = DiscordWebhook(url=WEBHOOK_URL)
    embed = DiscordEmbed(
        title="🚨 스팀 업데이트 감지!",
        description=f"**게임:** {name}\n**AppID:** {appid}\n**브랜치:** `{branch}`\n**Build ID:** {buildid}",
        color="03b2f8"
    )
    embed.add_embed_field(name="다운로드/분석용", value=f"SteamDB: [열기](https://steamdb.info/app/{appid}/patchnotes/)")
    webhook.add_embed(embed)
    webhook.execute()

if __name__ == "__main__":
    check_updates()
