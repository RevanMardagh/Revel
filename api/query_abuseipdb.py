from abuseipdb_wrapper import AbuseIPDB
from definitions import ROOT_DIR
#
#
# def check_abuseipdb(ips):
#     API_KEY = "ffc53215145b0aaddec3be4138ec4468e4fd57c20ee6f66d583bb00f45030ea81aef5d1b34c95530"
#     abuse = AbuseIPDB(api_key=API_KEY, db_file='../exports/abuseipdb.json')
#     abuse.colors_legend()
#
#     # ips = ["18.237.3.202", "14.103.172.199"]
#     # print(dir(abuse))
#     abuse.add_ip_list(ips)
#
#     print("Checking IP addresses:")
#     abuse.check()
#
#     print("\n\nResults:")
#     abuse.show(table_view=False)
#
#     # print("\n\nThe results have been exported as html")
#     # abuse.export_html_styled(f"{ROOT_DIR}/exports/abuseipdb.html")
# check_abuseipdb(["18.237.3.202", "14.103.172.199"])
#
#
def checkrep(ips):
    ABUSE_API_KEY = "ffc53215145b0aaddec3be4138ec4468e4fd57c20ee6f66d583bb00f45030ea81aef5d1b34c95530"
    abuse = AbuseIPDB(api_key=ABUSE_API_KEY, db_file=f'{ROOT_DIR}/exports/abuseipdb.json')
    abuse.add_ip_list(ips)
    abuse.check()

    abuse_scores = {}
    for ip in ips:
        # abuse.show(ip, table_view=False)
        report = abuse.get_db()
        print(ip, report.get(ip).get("abuseConfidenceScore"))
        abuse_scores[ip] = report.get(ip).get("abuseConfidenceScore")
        print(abuse_scores)



if __name__ == "__main__":
    # Simple test
    test_ips = ["8.8.8.8", "1.1.1.1", "5.135.75.243"]
    reputations = checkrep(test_ips)
    for ip, level in reputations.items():
        print(f"{ip}: {level}")
