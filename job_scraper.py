import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import telegram

KEYWORDS = [
    "ADAS", "Sensor Fusion", "Radar", "LiDAR", "Thermal Camera", "ROS", "ROS2",
    "Python", "C++", "MATLAB", "OpenCV", "Open3D", "YOLO", "Deep Learning", "AI",
    "ML", "Neural Networks", "Embedded Systems", "Autonomous Driving", "Perception",
    "Kalman Filter", "Computer Vision", "Automotive Safety", "SLAM", "Simulink"
]

def scrape_indeed():
    base_url = "https://de.indeed.com/jobs?q=werkstudent+OR+praktikum+OR+internship&l=Deutschland&sort=date"
    headers = {"User-Agent": "Mozilla/5.0"}
    jobs = []

    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    postings = soup.find_all('a', attrs={'data-hide-spinner': 'true'})

    for post in postings:
        title = post.text.strip()
        url = "https://de.indeed.com" + post['href']
        for kw in KEYWORDS:
            if kw.lower() in title.lower():
                jobs.append({
                    "Title": title,
                    "Link": url,
                    "Keyword": kw,
                    "Date": datetime.now().strftime('%Y-%m-%d'),
                    "Source": "Indeed"
                })
                break
    return jobs

def save_to_excel(jobs):
    df = pd.DataFrame(jobs)
    filename = "jobs_" + datetime.now().strftime('%Y%m%d') + ".xlsx"
    df.to_excel(filename, index=False)
    return filename

def send_telegram_message(file, jobs):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    bot = telegram.Bot(token=token)
    message = f"🚀 {len(jobs)} new jobs found in ADAS/ML/Automotive.\n\nSample:\n"
    for job in jobs[:3]:
        message += f"- {job['Title']}\n{job['Link']}\n\n"

    bot.send_message(chat_id=chat_id, text=message)
    bot.send_document(chat_id=chat_id, document=open(file, "rb"))

if __name__ == "__main__":
    jobs = scrape_indeed()
    if jobs:
        file = save_to_excel(jobs)
        send_telegram_message(file, jobs)
