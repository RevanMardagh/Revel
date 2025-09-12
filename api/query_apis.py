import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
import vt
import os
from abuseipdb_wrapper import AbuseIPDB
from mylibs.definitions import ROOT_DIR
from mylibs.settings import load_settings



# Load settings
settings = load_settings()

def get_abuseipdb_scores(ips, api_key=None):
    """
    Returns a dictionary of IPs to their abuseConfidenceScore from AbuseIPDB.
    Returns -1 if the API call fails (including invalid API key).
    """
    if api_key is None:
        api_key = settings.get("abuseipdb_key", "")

    abuse_scores = {}
    try:
        abuse = AbuseIPDB(api_key=api_key, db_file=os.path.join(ROOT_DIR, "db", "abuseipdb.json"))
        abuse.add_ip_list(ips)
        abuse.check()
        db_data = abuse.get_db()


        # If the db_data doesn't contain any of our IPs, assume API failure
        if not any(ip in db_data for ip in ips):
            print("AbuseIPDB API likely failed (check results missing)")
            for ip in ips:
                abuse_scores[ip] = -1
            return abuse_scores

        # Otherwise, return scores normally
        for ip in ips:
            score = db_data.get(ip, {}).get("abuseConfidenceScore", -1)
            abuse_scores[ip] = score

    except Exception as e:
        print("AbuseIPDB unexpected exception:", e)
        for ip in ips:
            abuse_scores[ip] = -1

    return abuse_scores



# --- VirusTotal function ---
#
# def get_virustotal_flags(ips, api_key=None):
#     api_key = settings.get("virustotal_key")
#     if not api_key:  # catches None or empty string
#
#     client = vt.Client(api_key)
#     vt_scores = {}
#
#     for ip in ips:
#         try:
#             ip_obj = client.get_object(f"/ip_addresses/{ip}")
#             stats = ip_obj.last_analysis_stats
#             vt_scores[ip] = {
#                 "malicious": stats.get("malicious", 0),
#                 "suspicious": stats.get("suspicious", 0),
#                 "total": sum(stats.values())
#             }
#         except vt.APIError as e:
#             # print(f"Error checking {ip}: {e}")
#             vt_scores[ip] = {"malicious": 0, "suspicious": 0, "total": 0}
#
#     client.close()
#     return vt_scores



def get_virustotal_flags(ips, api_key=None, max_workers=10):
    """
    Query VirusTotal for a list of IPs in parallel.
    Returns dict {ip: {malicious, suspicious, total}}
    Handles API errors and no internet connection gracefully.
    """

    if not api_key:
        api_key = settings.get("virustotal_key")
    if not api_key:
        # fallback API key (⚠️ better to avoid hardcoding secrets)
        print("VirusTotal API key not configured")

    def fetch(ip):
        try:
            client = vt.Client(api_key)
            try:
                ip_obj = client.get_object(f"/ip_addresses/{ip}")
                stats = ip_obj.last_analysis_stats or {}
                return ip, {
                    "malicious": stats.get("malicious", 0),
                    "suspicious": stats.get("suspicious", 0),
                    "total": sum(stats.values())
                }
            except (vt.APIError, vt.error.APIError):
                # API error → safe defaults
                return ip, {"malicious": 0, "suspicious": 0, "total": 0}
            finally:
                client.close()
        except (socket.gaierror, OSError, ConnectionError) as e:
            # No internet / DNS / network error
            return ip, {"malicious": -1, "suspicious": -1, "total": -1}

    vt_scores = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch, ip): ip for ip in ips}
        for future in as_completed(futures):
            ip, data = future.result()
            vt_scores[ip] = data

    return vt_scores





# --- Risk level function using only AbuseIPDB ---
def check_ip_reputation_levels(ips, abuse_scores):
    """
    Assigns a risk level to each IP based only on AbuseIPDB confidence score.
    Returns: { ip: "Safe"/"Low Risk"/"Medium Risk"/"High Risk"/"Malicious" }
    """
    # abuse_scores = get_abuseipdb_scores(ips)
    # print("Abuse score  ", abuse_scores)
    results = {}

    for ip, score in abuse_scores.items():
        if score == -1:
            results[ip] = "Unknown"
        elif score <= 3:
            results[ip] = "Safe"
        elif score < 20:
            results[ip] = "Low Risk"
        elif score < 50:
            results[ip] = "Medium Risk"
        elif score < 80:
            results[ip] = "High Risk"
        elif score > 80:
            results[ip] = "Malicious"

    print(results)
    return results

# Get the reports from Virustotal and AbuseIPDB
# def get_ip_report(ips):
#     """
#     Returns a dict mapping IPs to:
#     { ip: {"virustotal": {...}, "abuseipdb": ...} }
#     """
#     abuse_scores = get_abuseipdb_scores(ips)    # expected: {ip: score}
#     virustotal_flags = get_virustotal_flags(ips)  # expected: {ip: {malicious, suspicious, total}}
#     reputation = check_ip_reputation_levels(ips, abuse_scores)
#
#     combined = {}
#     for ip in ips:
#         combined[ip] = {
#             "virustotal": virustotal_flags.get(ip, {}),
#             "abuseipdb": abuse_scores.get(ip, "N/A"),
#             "reputation": reputation.get(ip, {})
#         }
#
#     return combined

def get_ip_report(ips):
    results = {}

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(get_abuseipdb_scores, ips): "abuseipdb",
            executor.submit(get_virustotal_flags, ips): "virustotal",
        }

        partial = {}
        for future in as_completed(futures):
            key = futures[future]
            partial[key] = future.result()

    abuse_scores = partial.get("abuseipdb", {})
    virustotal_flags = partial.get("virustotal", {})

    reputation = check_ip_reputation_levels(ips, abuse_scores)

    combined = {}
    for ip in ips:
        combined[ip] = {
            "virustotal": virustotal_flags.get(ip, {}),
            "abuseipdb": abuse_scores.get(ip, "N/A"),
            "reputation": reputation.get(ip, {})
        }

    return combined

if __name__ == "__main__":
    test_ips = ["8.8.8.8", "1.1.1.1", "5.135.75.243"]

    # reputations = check_ip_reputation_levels(test_ips)
    # # print("AbuseIPDB-based reputations:")
    # for ip, level in reputations.items():
    #     print(f"{ip}: {level}")

    # Optional: call VirusTotal separately elsewhere
    vt_flags = get_ip_report(test_ips)
    print("\nVirusTotal flagged counts:", vt_flags)
