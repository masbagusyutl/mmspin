import time
import requests
import datetime

# Fungsi untuk membaca token dari file data.txt
def read_tokens(file_path='data.txt'):
    with open(file_path, 'r') as file:
        tokens = [line.strip() for line in file]
    return tokens

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

# Fungsi untuk melakukan request tugas sign-in
def task_sign_in(headers):
    url = "https://memespin.net/api/v1/task/sign-in"
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print("Sign-in task completed successfully.")
    else:
        print("Failed to complete sign-in task.")

# Fungsi untuk melakukan request spin
def spin_lottery(headers, spins=5):
    url = "https://memespin.net/api/v1/game/roulette/lottery"
    for _ in range(spins):
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            print("Spin completed successfully.")
        else:
            print("Failed to complete spin.")
        time.sleep(1)  # Optional delay between spins

# Fungsi utama
def main():
    tokens = read_tokens()
    total_accounts = len(tokens)
    print(f"Total accounts: {total_accounts}")

    for index, token in enumerate(tokens, start=1):
        headers = {
            "Authorization": f"Bearer {token}"
        }
        print(f"\nProcessing account {index}/{total_accounts}")
        task_sign_in(headers)
        spin_lottery(headers, spins=5)
        task_sign_in(headers)
        spin_lottery(headers, spins=5)
        
        if index < total_accounts:
            print(f"Waiting for 5 seconds before switching to the next account...")
            time.sleep(5)

    print("All accounts processed. Starting 1-day countdown...")
    countdown_timer(24 * 60 * 60)
    print("Restarting process...")
    main()

if __name__ == "__main__":
    main()