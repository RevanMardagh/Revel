import vt
from mylibs.settings import load_settings
import os

# Load settings
settings = load_settings()

# --- AbuseIPDB function ---
from mylibs.settings import load_settings

# Load settings
settings = load_settings()

from abuseipdb_wrapper import AbuseIPDB
from mylibs.definitions import ROOT_DIR
from mylibs.settings import load_settings

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
        abuse = AbuseIPDB(api_key=api_key, db_file=os.path.join(ROOT_DIR, "exports", "abuseipdb.json"))
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
def get_virustotal_flags(ips, api_key=None):
    api_key = settings.get("virustotal_key")
    if not api_key:  # catches None or empty string
        api_key = "fd336c37705badcf8f1a3c69821aaf6c3b744d2e167e6bddc89da6927b2cecb0"

    client = vt.Client(api_key)
    vt_scores = {}

    for ip in ips:
        try:
            ip_obj = client.get_object(f"/ip_addresses/{ip}")
            stats = ip_obj.last_analysis_stats
            vt_scores[ip] = {
                "malicious": stats.get("malicious", 0),
                "suspicious": stats.get("suspicious", 0),
                "total": sum(stats.values())
            }
        except vt.APIError as e:
            print(f"Error checking {ip}: {e}")
            vt_scores[ip] = {"malicious": 0, "suspicious": 0, "total": 0}

    client.close()
    return vt_scores



# --- Risk level function using only AbuseIPDB ---
def check_ip_reputation_levels(ips):
    """
    Assigns a risk level to each IP based only on AbuseIPDB confidence score.
    Returns: { ip: "Safe"/"Low Risk"/"Medium Risk"/"High Risk"/"Malicious" }
    """
    abuse_scores = get_abuseipdb_scores(ips)
    print("Abuse score  ", abuse_scores)
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
def get_ip_report(ips):
    """
    Returns a dict mapping IPs to:
    { ip: {"virustotal": {...}, "abuseipdb": ...} }
    """
    abuse_scores = get_abuseipdb_scores(ips)    # expected: {ip: score}
    virustotal_flags = get_virustotal_flags(ips)  # expected: {ip: {malicious, suspicious, total}}

    combined = {}
    for ip in ips:
        combined[ip] = {
            "virustotal": virustotal_flags.get(ip, {}),
            "abuseipdb": abuse_scores.get(ip, "N/A")
        }

    return combined


if __name__ == "__main__":
    test_ips = ["8.8.8.8", "1.1.1.1", "5.135.75.243"]

    # reputations = check_ip_reputation_levels(test_ips)
    # # print("AbuseIPDB-based reputations:")
    # for ip, level in reputations.items():
    #     print(f"{ip}: {level}")

    # Optional: call VirusTotal separately elsewhere
    vt_flags = get_virustotal_flags(test_ips)
    print("\nVirusTotal flagged counts:", vt_flags)
