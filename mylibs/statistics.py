from collections import Counter, defaultdict
from mylibs.parser import parser

from more_itertools.recipes import unique


from collections import Counter, defaultdict

def ip_statistics(logs):
    """
    Analyze logs by remote_addr:
      - Count of each status code
      - Total requests
      - 4xx error ratio (as 'X/Y')
      - Raw ip_counts (total requests per IP)
      - User-Agent counts per IP
    """
    status_counts = defaultdict(Counter)
    ip_counts = Counter(entry["remote_addr"] for entry in logs)
    ua_counts = defaultdict(Counter)  # store user-agent counts per IP

    # Count statuses and user-agents per IP
    for log in logs:
        addr = log["remote_addr"]
        status = log["status"]
        ua = log.get("user_agent", "Unknown")  # fallback if field missing

        status_counts[addr][status] += 1
        ua_counts[addr][ua] += 1

    # Prepare results
    results = {}
    for addr, counts in status_counts.items():
        total = sum(counts.values())
        errors_4xx = sum(c for s, c in counts.items() if 400 <= s < 500)
        ratio_str = f"{errors_4xx}/{total} ({errors_4xx/total:.2%})"

        sorted_status_counts = dict(sorted(counts.items(), key=lambda x: x[0]))
        sorted_ua_counts = dict(ua_counts[addr].items(), key=lambda x: x[1], reverse=True)

        results[addr] = {
            "status_counts": sorted_status_counts,
            "total_requests": total,
            "4xx_ratio": ratio_str,
            "ip_count": ip_counts[addr],
            "user_agents": sorted_ua_counts  # add user-agent info
        }
    print(results)
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
    # ip_statistics(dat)
    log_stats, ip_stats = log_statistics(dat)
