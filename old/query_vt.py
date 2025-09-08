import vt

def check_virustotal(ips):
    client = vt.Client("fd336c37705badcf8f1a3c69821aaf6c3b744d2e167e6bddc89da6927b2cecb0")
    analysis_results = []

    for ip in ips:
        try:
            ip_obj = client.get_object(f"/ip_addresses/{ip}")
            # print(ip_obj.last_analysis_stats)
            # print("Reputation:", ip_obj.reputation)
            analysis_results.append(ip_obj)
        except vt.APIError as e:
            print(f"Error checking {ip}: {e}")

    client.close()
    return analysis_results

# Example usage
url2 = check_virustotal(["102.40.23.30", "1.1.1.1"])

for result in url2:
    print(result.last_analysis_stats)
