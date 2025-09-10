import json


def parser(file):
    if file is None:
        print("No file specified, exiting...")
        return -1

    parsed_logs = []

    with open(file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Expect 3 tab-separated parts
            parts = line.split("\t", 2)
            if len(parts) != 3:
                continue

            # Parse JSON
            try:
                data = json.loads(parts[2])
            except json.JSONDecodeError:
                continue

            parsed_logs.append({
                "timestamp_ms": int(parts[0]),
                "iso_time": parts[1],
                **data
            })

    # If no valid lines were parsed, return -1
    if not parsed_logs:
        return []

    return parsed_logs

# print(parser("C:/Users/Ravan/PycharmProjects/LogAnalyzer/logs/access_log.txt"))