from google import genai

from mylibs.statistics import ip_statistics
import mylibs.parser as parser


# dat = parser.parser("../logs/new_log.txt")
# logs_dict = ip_statistics(dat)
#
# logs_dict = ip_statistics(["5.135.75.243", "13.56.237.135"])

prompt = f"""
You are a cybersecurity analyst. I will provide a dictionary containing IP addresses and their log statistics, including HTTP status counts, total requests, 4xx ratios, and user agents.

Your task is to write a concise, readable overview in a few paragraphs. Focus on:
- Identifying the tools or automated scripts used (e.g., dirbuster, nikto, bots).  
- Explaining what the IPs were doing (e.g., scanning, probing, brute-force attempts).  
- Highlighting any suspicious or unusual patterns in traffic or status codes.  
- Summarizing the overall activity and risk in an understandable way.

Do not return JSON or tables. Just write coherent paragraphs.

Here is the data:
{logs_dict}
"""


# Your API key in a Python variable
api_key = "AIzaSyBfIbqkLpHsxZdubj-_IVk-t2OOPKw47r4"

# Pass it to the client
client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)





print(response.text)