import os
import subprocess
import requests
import json
from datetime import datetime, timezone
import generate_report # Re-using the logic from the previous turn

# Configuration
TELEGRAM_BOT_TOKEN = "[REDACTED-TELEGRAM-TOKEN]"
TELEGRAM_CHAT_ID = "-1003740520259" # The group chat ID
RCLONE_REMOTE = "gdrive:arifOS/outputs"

def handle_report():
    print("Starting GEOX Report Generation & Delivery Pipeline...")
    
    # Step 1: Generate PDF
    # The generate_report.py already has create_pdf() function
    output_filename = "NW_Sabah_Geological_Synthesis.pdf"
    generate_report.create_pdf(output_filename)
    print(f"PDF generated: {output_filename}")
    
    # Step 2: Upload to Google Drive via rclone
    print(f"Uploading {output_filename} to Google Drive...")
    try:
        subprocess.run(["rclone", "copy", output_filename, RCLONE_REMOTE], check=True)
        print("Upload successful.")
    except subprocess.CalledProcessError as e:
        print(f"rclone upload failed: {e}")
        return

    # Step 3: Get public link from Google Drive
    print("Generating public shareable link...")
    try:
        remote_path = f"{RCLONE_REMOTE}/{output_filename}"
        link_result = subprocess.run(["rclone", "link", remote_path], capture_output=True, text=True, check=True)
        public_url = link_result.stdout.strip()
        print(f"Public link: {public_url}")
    except subprocess.CalledProcessError as e:
        print(f"rclone link failed: {e}")
        public_url = "Unable to generate link."

    # Step 4: Send to Telegram as Document with Link in Caption
    print("Sending document to Telegram...")
    caption = (
        f"📄 *NW Sabah Geological Synthesis Report*\n"
        f"📅 Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
        f"🔗 [View on Google Drive]({public_url})\n\n"
        f"DITEMPA BUKAN DIBERI | arifOS Trinity"
    )
    
    try:
        with open(output_filename, "rb") as f:
            resp = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument",
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "caption": caption,
                    "parse_mode": "Markdown"
                },
                files={"document": f}
            )
        
        if resp.status_code == 200:
            print("Telegram delivery successful.")
        else:
            print(f"Telegram API error ({resp.status_code}): {resp.text}")
    except Exception as e:
        print(f"Telegram delivery failed: {e}")

if __name__ == "__main__":
    handle_report()
