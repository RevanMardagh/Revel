import vt

def check_virustotal(ips):
    client = vt.Client("6959c5e658d3ec7fea72475347b4b8025c4a8de00767317f2e0e8c1978f0bab4")

    analysis_results = []

    for ip in ips:
        url_id = vt.url_id(ip)
        url = client.get_object("/urls/{}", url_id)
        # print(url.last_analysis_stats)
        print(url.reputation)
        # print(dir(url))
        # analysis_results.append(url)

        # print(url.last_analysis_results)


    client.close()
    return analysis_results
url2 = check_virustotal(["102.40.23.30"])

# print(url2)


import requests
