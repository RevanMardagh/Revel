from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from api.query_apis import get_ip_report, check_ip_reputation_levels

def ip_statistics(logs):
    status_counts = defaultdict(Counter)
    ip_counts = Counter(entry["remote_addr"] for entry in logs)
    ua_counts = defaultdict(Counter)

    for log in logs:
        addr = log["remote_addr"]
        status = log["status"]
        ua = log.get("user_agent", "Unknown")
        status_counts[addr][status] += 1
        ua_counts[addr][ua] += 1

    # Pull IP reports in parallel
    ip_list = list(ip_counts.keys())

    # --- get reputation levels ---
    # reputation = check_ip_reputation_levels(ip_list)  # returns {'ip': 'Malicious', ...}

    # --- get detailed reports from VT & AbuseIPDB ---
    reports = {}
    def fetch_report(ip):
        try:
            return ip, get_ip_report([ip]).get(ip, {})
        except Exception:
            return ip, {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ip = {executor.submit(fetch_report, ip): ip for ip in ip_list}
        for future in as_completed(future_to_ip):
            ip, report = future.result()
            reports[ip] = report
    # reports = get_ip_report(ip_list)


    results = {}
    for addr, counts in status_counts.items():
        total = sum(counts.values())
        errors_4xx = sum(c for s, c in counts.items() if 400 <= s < 500)
        ratio_str = f"{errors_4xx}/{total} ({errors_4xx/total:.2%})"

        sorted_status_counts = dict(sorted(counts.items(), key=lambda x: x[0]))
        sorted_ua_counts = dict(sorted(ua_counts[addr].items(), key=lambda x: x[1], reverse=True))

        vt_data = reports.get(addr, {}).get("virustotal", {})
        if vt_data:
            total_flags = sum(vt_data.values())
            malicious_flags = vt_data.get("malicious", 0)
            suspicious_flags = vt_data.get("suspicious", 0)
            if total_flags > 0:
                vt_formatted = f"Total: {total_flags}, Malicious: {malicious_flags}, Suspicious: {suspicious_flags}"
            else:
                vt_formatted = f"Virustotal API Quota exceeded"
        else:
            vt_formatted = "N/A"

        abuse_score = reports.get(addr, {}).get("abuseipdb", "N/A")
        reputation = reports.get(addr, {}).get("reputation", "Unknown")

        # --- merge reputation ---
        results[addr] = {
            "status_counts": sorted_status_counts,
            "total_requests": total,
            "4xx_ratio": ratio_str,
            "ip_count": ip_counts[addr],
            "user_agents": sorted_ua_counts,
            "virustotal": vt_formatted,
            "abuseipdb": abuse_score,
            "reputation": reputation
        }

    return results



def log_statistics(parsed_data):
    total_requests = len(parsed_data)
    unique_ips = len(set(entry["remote_addr"] for entry in parsed_data))

    error_count = sum(1 for e in parsed_data if str(e["status"]).startswith("4"))
    # error_count = sum(1 for e in parsed_data if int(e["status"]) >= 400 and int(e["status"]) < 500)
    error_rate = f"{error_count}/{total_requests} ({error_count/total_requests:.2%})"
    # error_rate = error_count / total_requests


    ip_stats = ip_statistics(parsed_data)
    # print(ip_stats)
    #
    # print(f"Total requests: {total_requests}")
    # print(f"Unique IPs: {unique_ips}")
    # print(f"Errors: {error_count}")
    # print(f"4xx ratio within the log: {error_rate}\n\r\n\r")
    #
    # for addr, data in ip_stats.items():
    #     print(f"{addr}: {data}")


    return {
        "total_requests": total_requests,
        "unique_ips": unique_ips,
        "error_count": error_count,
        "error_rate": error_rate

    }, ip_stats


if __name__ == "__main__":
    import parser
    dat = parser.parser("../logs/new_log.txt")
    ip_statistics(dat)
    # log_stats, ip_stats = log_statistics(dat)
