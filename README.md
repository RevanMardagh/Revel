# Revel Log Analyzer
~ by Ravan Ismayilov

A desktop application for analyzing log files, generating per-IP statistics, and creating AI-assisted summaries. Built with Python, PyQt6, and blood of the innocent.
## Features

- 📂 File selection for importing log files
- 📄 List all logs, color coded to reputation (Red - Malicious, Green - Safe, etc.) 
- 📊 Log statistics (status codes, requests, error ratios, per-IP data)
- 🤖 AI-generated overview of log activity (via Gemini API)
- 📈 Detailed per-IP breakdown of logs with AbuseIPDB, Virustotal and AI analysis
- 🧾 Export results to TXT, MD, DOCX, HTML
- 🖥️ Cross-platform (Windows & Linux)
- ⚙️ Settings menu to change API keys, disable/enable AI overview



- The application remembers the last saved settings, including the last used filepath


---

## Usage

### Execution

1. Run `main.py` to start the program
2. **Browse** to select a log file, then press **Select** to start analyzing the file
    
### Settings

Modifying settings should be fairly simple. You can press **show** to see/modify API keys as well as toggle AI overview on/off

### Overview page

- Here, you can see every log line parsed and displayed on a table
- The rows are color coded according to the IP addresses' AbuseIPDB reputation
- Filter based on row text, status codes, and risk level

### Statistics page

- Reports of each IP showing:
    - Total requests within the log
    - 4xx error ratio
    - The count of each status code for the IP
    - Every user agent and the amount of times they have been used (Note: You have to resize the row to see all user agents)
    - Virustotal report (Malicious and Suspicious flags) (Not working because we are blocked by Virustotal LMAO)
    - AbuseIPDB score
    - Conclusion upon the severity of the IP address


### AI overview

- If you've enabled AI overview in the settings, useful information will be passed to Google's Gemini AI model to review the logs and give a comprehensive overview
 
- The AI review contains:
    - Executive Summary
    - Detailed analysis of Observed activity - tools used, vulnerabilities exploited (CVEs), attack patterns
    - Overall activity and summary
    - Mitigation Strategies
- Rarely, if the Gemini servers are overloaded, your request might be blocked. In that case, re-run the program, and it should work.

### Export

- You can export as 1 or more of these file types
    - MD, TXT, HTML, DOCX, PDF (pdf doesnt work yet)
- They will be created in the folder you choose, in a sub folder with the `File Base Name` you set
- If there already is a folder with the same name, "_1" is appended to the folder name. 
    The number is incremented if there are multiple duplicates
- Press **Refresh Data from AI** after AI has loaded its summary to prepare it to be exported. 

---

## Dependencies

- All required Python libraries are listed in the `requirements.txt` file.

Run `pip install -r requirements.txt` to install all dependencies

---

## Notes

- For some insane reason, the script does 3 AbuseIPDB checks, which slow down the script. For now, you will just have to wait a few seconds after pressing `Select`. 
  I will get down to fix this, eventually.
- The tables in exported .docx files are huge, therefore they overflow to multiple pages. Genuinely no idea how to fix this. Pandoc is weird