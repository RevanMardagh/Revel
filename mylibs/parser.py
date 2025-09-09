import json


def parser(file):
    # file = get_file()
    # print(file)
    if file is None:
        print("No file specified, exiting...")
        return

    parsed_logs = []

    with open(file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Split into 3
            parts = line.split("\t", 2)
            if len(parts) != 3:
                continue  # skip bad lines

            # Convert to JSON
            try:
                data = json.loads(parts[2])
            except json.JSONDecodeError:
                # print(f"Skipping line  - {line} - malformed line")
                continue

            parsed_logs.append({
                "timestamp_ms": int(parts[0]),
                "iso_time": parts[1],
                **data
            })

    # ---
    # unique_addresses = {entry["remote_addr"] for entry in parsed_logs}

    # print(parsed_logs)
    # print("IP addresses and their counts:")
    # for ip, count in ip_counts.items():
    #     print(f"{ip}:\t{count}")

    # folder_name = "exports\\Log_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # os.makedirs(os.path.join(ROOT_DIR, folder_name))
    #
    # with open(f"{ROOT_DIR}\\{folder_name}\\parsed_logs.txt", "w") as f:
    #     for line in parsed_logs:
    #         f.write(str(line) + "\n")

    return parsed_logs



# parser()