import requests
from bs4 import BeautifulSoup

def get_talos_reputation(ip):
    url = f"https://talosintelligence.com/reputation_center/lookup?search={ip}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://talosintelligence.com/",
        "Connection": "keep-alive",
    }

    session = requests.Session()
    response = session.get(url, headers=headers)

    if response.status_code != 200:
        return f"Error: status code {response.status_code}"

    soup = BeautifulSoup(response.text, "html.parser")
    reputation_div = soup.find("div", class_="reputation-status")
    if reputation_div:
        return reputation_div.get_text(strip=True)
    else:
        return "Reputation info not found"

# Example
ips = ["8.8.8.8", "1.1.1.1"]
for ip in ips:
    print(f"{ip}: {get_talos_reputation(ip)}")
