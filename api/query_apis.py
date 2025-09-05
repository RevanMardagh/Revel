import vt
from abuseipdb_wrapper import AbuseIPDB
from definitions import ROOT_DIR


# --- AbuseIPDB function ---
def get_abuseipdb_scores(ips, api_key=None):
    """
    Returns a dictionary of IPs to their abuseConfidenceScore from AbuseIPDB.
    { ip: score }
    """
    if api_key is None:
        api_key = "ffc53215145b0aaddec3be4138ec4468e4fd57c20ee6f66d583bb00f45030ea81aef5d1b34c95530"

    abuse = AbuseIPDB(api_key=api_key, db_file=f'{ROOT_DIR}/exports/abuseipdb.json')
    abuse.add_ip_list(ips)
    abuse.check()

    abuse_scores = {}
    db_data = abuse.get_db()
    for ip in ips:
        score = db_data.get(ip, {}).get("abuseConfidenceScore", 0)
        abuse_scores[ip] = score

    return abuse_scores


# --- VirusTotal function ---
def get_virustotal_flags(ips, api_key=None):
    """
    Returns a dictionary of IPs to number of engines flagging them as malicious or suspicious.
    { ip: flagged_count }
    """
    if api_key is None:
        api_key = "6959c5e658d3ec7fea72475347b4b8025c4a8de00767317f2e0e8c1978f0bab4"

    client = vt.Client(api_key)
    vt_scores = {}

    for ip in ips:
        try:
            ip_obj = client.get_object(f"/ip_addresses/{ip}")
            mal = ip_obj.last_analysis_stats.get("malicious", 0)
            sus = ip_obj.last_analysis_stats.get("suspicious", 0)
            vt_scores[ip] = mal + sus
        except Exception:
            vt_scores[ip] = 0

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
        if score <= 3:
            results[ip] = "Safe"
        elif score < 20:
            results[ip] = "Low Risk"
        elif score < 50:
            results[ip] = "Medium Risk"
        elif score < 80:
            results[ip] = "High Risk"
        else:
            results[ip] = "Malicious"
    # print(results)
    return results


if __name__ == "__main__":
    test_ips = ["8.8.8.8", "1.1.1.1", "5.135.75.243"]

    reputations = check_ip_reputation_levels(test_ips)
    # print("AbuseIPDB-based reputations:")
    for ip, level in reputations.items():
        print(f"{ip}: {level}")

    # Optional: call VirusTotal separately elsewhere
    vt_flags = get_virustotal_flags(test_ips)
    print("\nVirusTotal flagged counts:", vt_flags)
