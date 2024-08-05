import time
import requests
import json

# Fungsi untuk membaca data akun dari file data.txt
def read_accounts(file_path='data.txt'):
    accounts = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for i in range(0, len(lines), 3):
            if i + 2 < len(lines):
                telegram_data = lines[i].strip()
                auth_token = lines[i+1].strip().split(' ')[1]  # remove "Authorization: "
                cookie = lines[i+2].strip()
                accounts.append((telegram_data, auth_token, cookie))
    return accounts

# Fungsi untuk menampilkan hitung mundur
def countdown_timer(seconds):
    while seconds:
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        timer = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)
        print(f'\rCountdown: {timer}', end="")
        time.sleep(1)
        seconds -= 1
    print()

# Fungsi untuk melakukan request login
def login_task(telegram_data, auth_token, cookie):
    url = "https://memespin.net/api/v1/user/telegram/login"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
        "Cache-Control": "no-cache",
        "Content-Length": str(len(telegram_data)),
        "Content-Type": "application/json",
        "Origin": "https://memespin.net",
        "Pragma": "no-cache",
        "Priority": "u=1, i",
        "Referer": "https://memespin.net/",
        "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126", "Microsoft Edge WebView2";v="126"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    response = requests.post(url, headers=headers, data=telegram_data)
    if response.status_code == 200:
        print("Login task completed successfully.")
        try:
            data = response.json()
        except json.JSONDecodeError:
            print("Error decoding JSON response.")
            return None
        return data.get('data', {}).get('access_token')
    else:
        print("Failed to complete login task.")
        return None

# Fungsi untuk melakukan tugas sign-in
def sign_in_task(headers):
    url = "https://memespin.net/api/v1/task/sign-in"
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print("Sign-in task completed successfully.")
    else:
        print("Failed to complete sign-in task.")

# Fungsi untuk mendapatkan info akun
def get_account_info(headers):
    url = "https://memespin.net/api/v1/user/info"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            data = response.json().get('data', {})
        except json.JSONDecodeError:
            print("Error decoding JSON response.")
            return 0
        telegram_id = data.get('telegram_id')
        game_coins = data.get('game_coins')
        diamonds = data.get('diamonds')
        game_times = data.get('game_times')
        print(f"Telegram ID: {telegram_id}")
        print(f"Game Coins: {game_coins}")
        print(f"Diamonds: {diamonds}")
        print(f"Game Times: {game_times}")
        return game_times
    else:
        print("Failed to get account info.")
        return 0

# Fungsi untuk melakukan spin
def spin_lottery(headers, spins):
    url = "https://memespin.net/api/v1/game/roulette/lottery"
    successful_spins = 0
    for i in range(spins):
        print(f"Spin ke-{i + 1}")
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            try:
                data = response.json().get('data', {})
            except json.JSONDecodeError:
                print("Error decoding JSON response.")
                continue
            print(f"prize_token: {data.get('prize_token')}")
            print(f"amount: {data.get('amount')}")
            print(f"usd_amount: {data.get('usd_amount')}")
            successful_spins += 1
            time.sleep(5)  # Jeda setelah spin
        else:
            print("Failed to complete spin.")
            time.sleep(5)  # Jeda jika gagal spin
    return successful_spins

# Fungsi untuk memproses satu akun
def process_single_account(telegram_data, auth_token, cookie):
    new_auth_token = login_task(telegram_data, auth_token, cookie)
    if not new_auth_token:
        return
    
    headers = {
        "Authorization": f"Bearer {new_auth_token}",
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
        "Cache-Control": "no-cache",
        "Content-Length": "0",
        "Origin": "https://memespin.net",
        "Pragma": "no-cache",
        "Priority": "u=1, i",
        "Referer": "https://memespin.net/",
        "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126", "Microsoft Edge WebView2";v="126"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    sign_in_task(headers)
    
    game_times = get_account_info(headers)
    if game_times == 0:
        print("Belum ada kesempatan spin untuk akun ini.")
        return
    
    spins_needed = game_times
    successful_spins = spin_lottery(headers, spins_needed)

    if successful_spins == game_times:
        print("Kesempatan spin sudah berhasil dilaksanakan semua.")
    else:
        print("Belum semua kesempatan spin dilaksanakan.")

    return new_auth_token

# Fungsi utama untuk memproses semua akun
def process_all_accounts():
    accounts = read_accounts()
    total_accounts = len(accounts)
    print(f"Total accounts: {total_accounts}")

    for index, (telegram_data, auth_token, cookie) in enumerate(accounts, start=1):
        print(f"\nProcessing account {index}/{total_accounts}")
        new_auth_token = process_single_account(telegram_data, auth_token, cookie)
        
        if new_auth_token:
            # Update token di file jika berhasil
            with open('data.txt', 'r') as file:
                lines = file.readlines()
            with open('data.txt', 'w') as file:
                for i in range(0, len(lines), 3):
                    if i + 1 < len(lines):
                        if lines[i+1].strip().split(' ')[1] == auth_token:
                            lines[i+1] = f"Authorization: {new_auth_token}\n"
                    file.write(lines[i])
                    file.write(lines[i+1])
                    file.write(lines[i+2])
        
        if index < total_accounts:
            print(f"Waiting for 5 seconds before switching to the next account...")
            time.sleep(5)

    print("All accounts processed. Starting 1-hour countdown...")
    countdown_timer(3600)
    print("Restarting process...")
    process_all_accounts()

# Fungsi utama
def main():
    print("Starting process...")
    process_all_accounts()

if __name__ == "__main__":
    main()
