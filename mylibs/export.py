import os
import shutil
import pypandoc
from tabulate import tabulate  # For nice tables in Markdown
from mylibs.settings import load_settings

def get_unique_output_dir(base_dir: str) -> str:
    """
    Returns a directory path that doesn't exist yet.
    If base_dir exists, appends _1, _2, etc.
    """
    unique_dir = base_dir
    counter = 1
    while os.path.exists(unique_dir):
        unique_dir = f"{base_dir}_{counter}"
        counter += 1
    os.makedirs(unique_dir, exist_ok=True)
    return unique_dir

def export_logs_and_ai(
    log_stats: dict,
    ip_stats: dict,
    ai_text: str = None,
    output_dir: str = os.path.join("exports", "logs"),
    base_name: str = "log_report",
    formats: list = None
):
    """
    Export logs + AI overview into multiple formats.
    :param formats: list of file types to export, e.g., ["md","txt","html","docx","pdf"]
    """
    formats = formats or ["md", "txt", "html", "docx", "pdf"]

    output_dir = os.path.join(output_dir, base_name)
    output_dir = get_unique_output_dir(output_dir)

    # --- Prepare Markdown content ---
    md_lines = []

    # --- Log statistics summary ---
    total_requests = log_stats.get("total_requests", 0)
    error_count = log_stats.get("error_count", 0)
    error_rate = log_stats.get("error_rate", 0)
    if isinstance(error_rate, (int, float)):
        error_rate_str = f"{error_rate:.2%}"
    else:
        error_rate_str = str(error_rate)

    md_lines.append("# Log Statistics Summary\n")
    md_lines.append(f"- Total Requests: {total_requests}")
    md_lines.append(f"- Error Count: {error_count}")
    md_lines.append(f"- Error Rate: {error_rate_str}\n")

    # --- IP table ---
    md_lines.append("## Per-IP Statistics\n")
    table_data = []
    headers = ["IP", "Total Requests", "4xx Ratio", "Status Counts", "VirusTotal", "AbuseIPDB"]

    for ip, stats in ip_stats.items():
        total = stats.get("total_requests", 0)
        ratio = stats.get("4xx_ratio", "0/0")
        status_counts = stats.get("status_counts", {})
        virustotal = stats.get("virustotal", "N/A")
        abuseipdb = stats.get("abuseipdb", "N/A")
        table_data.append([ip, total, ratio, status_counts, virustotal, abuseipdb])

    md_table = tabulate(table_data, headers=headers, tablefmt="github")
    md_lines.append(md_table + "\n")

    # --- AI Overview ---
    settings = load_settings()
    ai_allowed = settings.get("ai_allowed", False)

    if ai_text and ai_allowed:
        md_lines.append("## AI Overview\n")
        md_lines.append(ai_text)

    md_content = "\n".join(md_lines)

    # --- Export Markdown ---
    if "md" in formats:
        md_file = os.path.join(output_dir, f"{base_name}.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

    # --- Export TXT ---
    if "txt" in formats:
        txt_file = os.path.join(output_dir, f"{base_name}.txt")
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(md_content)

    # --- Export HTML ---
    if "html" in formats:
        html_file = os.path.join(output_dir, f"{base_name}.html")
        css_file = os.path.join("exports", "template", "style.css")
        try:
            pypandoc.convert_text(
                md_content,
                "html",
                format="md",
                outputfile=html_file,
                extra_args=[
                    f"--css={css_file}",
                    "--embed-resources",
                    "--standalone"
                ]
            )
        except Exception as e:
            print(f"⚠️ HTML export failed: {e}")

    # --- Export DOCX ---
    if "docx" in formats:
        docx_file = os.path.join(output_dir, f"{base_name}.docx")
        reference_docx = os.path.join("exports", "template", "template.docx")
        try:
            pypandoc.convert_text(
                md_content,
                "docx",
                format="md",
                outputfile=docx_file,
                extra_args=[
                    "--standalone",
                    f"--reference-doc={reference_docx}"
                ]
            )
        except Exception as e:
            print(f"⚠️ DOCX export failed: {e}")

    # --- Export PDF ---
    if "pdf" in formats:
        pdf_file = os.path.join(output_dir, f"{base_name}.pdf")
        if shutil.which("pdflatex"):
            try:
                pypandoc.convert_text(
                    md_content,
                    "pdf",
                    format="md",
                    outputfile=pdf_file,
                    extra_args=["--standalone"]
                )
            except Exception as e:
                print(f"⚠️ PDF export failed: {e}")
        else:
            print("⚠️ Skipped PDF export (pdflatex not installed)")

    print(f"✅ Exported to {output_dir} ({', '.join(formats)})")
