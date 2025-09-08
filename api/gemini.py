# ai_overview.py
from google import genai
import threading

def generate_ai_overview(logs_dict, api_key: str) -> str:
    """
    Generates a cybersecurity overview of IP statistics using Google GenAI.

    :param logs_dict: Dictionary with IP addresses and their log stats
    :param api_key: Your Google GenAI API key
    :return: Generated overview text or error message
    """
    prompt = f"""
    You are a cybersecurity analyst. I will provide a dictionary containing IP addresses and their log statistics, including HTTP status counts, total requests, 4xx ratios, and user agents.

    Your task is to write a concise, readable overview in a few paragraphs. Focus on:
    - Identifying the tools or automated scripts used (e.g., dirbuster, nikto, nmap, bots).  
    - Explaining what the IPs were doing (e.g., scanning, probing, brute-force attempts).  
    - Highlighting any suspicious or unusual patterns in traffic or status codes.  
    - Summarizing the overall activity and risk in an understandable way.
    - For malicious IPs, you can give individual summaries. The Virustotal and AbuseIPBD scores will be provided for you
    - Provide mitigation strategies.
    - Format it in a readable, beautiful way in markdown

    Do not return JSON or tables. Just write coherent paragraphs.

    Here is the data:
    {logs_dict}
    """

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )


        return response.text
    # except ServerError as e:
    #     return f"Error: Google GenAI server is currently unavailable. Details: {str(e)}"
    except Exception as e:
        return f"You've disabled AI, or Google Gemini servers are unavailable"
