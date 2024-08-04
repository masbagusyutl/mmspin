import time
import requests
import json

# Fungsi untuk membaca data akun dari file data.txt
def read_accounts(file_path='data.txt'):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    accounts = []
    for i in range(0, len(lines), 3):
        telegram_data = lines[i].strip()
        auth_token = lines[i+1].strip().replace('Authorization: ', '')  # remove "Authorization: "
        cookie = lines[i+2].strip()
        accounts.append((telegram_data, auth_token, cookie))
    return accounts

# Fungsi untuk menyimpan akun dengan token baru ke file data.txt
def save_accounts(accounts, file_path='data.txt'):
    with open(file_path, 'w') as file:
        for telegram_data, auth_token, cookie in accounts:
            file.write(f"{telegram_data}\nAuthorization: {auth_token}\n{cookie}\n")

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

# Fungsi untuk tugas login dan memperbarui token
def login_task(telegram_data, auth_token, cookie):
    url = "https://memespin.net/api/v1/user/telegram/login"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Cookie": cookie,
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
        "Cache-Control": "no-cache",
        "Origin": "https://memespin.net",
        "Pragma": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
    }
    response = requests.post(url, headers=headers, data=json.dumps({"telegram_data": telegram_data}))
    if response.status_code == 200:
        return response.json()['data']['access_token']
    else:
        print("Failed to login and update token.")
        return None

# Fungsi untuk mendapatkan informasi akun
def get_account_info(headers):
    url = "https://memespin.net/api/v1/user/info"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()['data']
        print(f"telegram_id: {data['telegram_id']}")
        print(f"game_coins: {data['game_coins']}")
        print(f"diamonds: {data['diamonds']}")
        print(f"game_times: {data['game_times']}")
        return data['game_times']
    else:
        print("Failed to get account info.")
        return 0

# Fungsi untuk melakukan request spin
def spin_lottery(headers, spins):
    url = "https://memespin.net/api/v1/game/roulette/lottery"
    success_spins = 0

    for attempt in range(3):  # Maximum 3 attempts
        for spin_num in range(spins):
            print(f"Spin ke-{spin_num + 1}")
            response = requests.post(url, headers=headers)
            if response.status_code == 200:
                data = response.json()['data']
                print(f"prize_token: {data['prize_token']}")
                print(f"amount: {data['amount']}")
                print(f"usd_amount: {data['usd_amount']}")
                success_spins += 1
            else:
                print("Failed to complete spin.")
            time.sleep(1)  # Optional delay between spins

        if success_spins >= spins:
            break  # Exit if the required spins are successful

# Fungsi untuk memproses satu akun
def process_single_account(telegram_data, auth_token, cookie):
    new_token = login_task(telegram_data, auth_token, cookie)
    if new_token:
        auth_token = new_token  # update token
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
        "Cache-Control": "no-cache",
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
    game_times = get_account_info(headers)
    spin_lottery(headers, spins=game_times)
    return auth_token

# Fungsi utama untuk memproses semua akun
def process_all_accounts():
    accounts = read_accounts()
    total_accounts = len(accounts)
    print(f"Total accounts: {total_accounts}")

    updated_accounts = []
    for index, (telegram_data, auth_token, cookie) in enumerate(accounts, start=1):
        print(f"\nProcessing account {index}/{total_accounts}")
        new_auth_token = process_single_account(telegram_data, auth_token, cookie)
        updated_accounts.append((telegram_data, new_auth_token, cookie))

        if index < total_accounts:
            print(f"Waiting for 5 seconds before switching to the next account...")
            time.sleep(5)

    save_accounts(updated_accounts)
    print("All accounts processed. Starting 1-day countdown...")
    countdown_timer(24 * 60 * 60)
    print("Restarting process...")
    main()

# Fungsi utama yang memberikan pilihan kepada pengguna
def main():
    choice = input("Do you want to process a single account? (yes/no): ").strip().lower()

    if choice == 'yes':
        account_index = int(input("Enter the account number to process (1-based index): ")) - 1
        accounts = read_accounts()
        if 0 <= account_index < len(accounts):
            telegram_data, auth_token, cookie = accounts[account_index]
            new_auth_token = process_single_account(telegram_data, auth_token, cookie)
            accounts[account_index] = (telegram_data, new_auth_token, cookie)
            save_accounts(accounts)
        else:
            print("Invalid account number.")
    else:
        process_all_accounts()

if __name__ == "__main__":
    main()
