from collections import Counter, defaultdict


def log_statistics(logs):
    """
    Analyze logs by remote_addr:
      - Count of each status code
      - Total requests
      - 4xx error ratio (as 'X/Y')
      - Raw ip_counts (total requests per IP)
    """
    status_counts = defaultdict(Counter)
    ip_counts = Counter(entry["remote_addr"] for entry in logs)

    # Count statuses per IP
    for log in logs:
        addr = log["remote_addr"]
        status = log["status"]
        status_counts[addr][status] += 1

    # Prepare results
    results = {}
    for addr, counts in status_counts.items():
        total = sum(counts.values())
        errors_4xx = sum(c for s, c in counts.items() if 400 <= s < 500)
        ratio_str = f"{errors_4xx}/{total}"
        results[addr] = {
            "status_counts": dict(counts),
            "total_requests": total,
            "4xx_ratio": ratio_str,
            "ip_count": ip_counts[addr]  # add Counter result
        }

    for addr, data in results.items():
        print(f"{addr}: {data}")

    return results


import parser
dat = parser.parser("../logs/new_log.txt")
log_statistics(dat)


