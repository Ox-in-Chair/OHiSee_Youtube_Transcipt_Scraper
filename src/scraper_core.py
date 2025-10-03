#!/usr/bin/env python3
"""YouTube Transcript Scraper - Core Engine"""
import os, re, sys, json, yt_dlp
from time import sleep
from datetime import datetime
from pathlib import Path
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class TranscriptScraper:
    def __init__(self, output_dir="transcripts", callback=None):
        self.output_dir = output_dir
        self.callback = callback
        self.driver = None
        Path(self.output_dir).mkdir(exist_ok=True)

    def _log(self, msg):
        if self.callback:
            self.callback(msg)
        else:
            print(msg)

    def sanitize_filename(self, text, max_len=80):
        text = re.sub(r'[\r\n]+', ' ', text).strip()
        text = re.sub(r'[\\/*?:"<>|]', '', text)
        text = re.sub(r'\s+', '_', text)
        return text[:max_len] or "untitled"

    def search_videos(self, query, max_results=10, search_filter=""):
        # Note: yt-dlp's ytsearch doesn't support filters in URL
        # Filters are ignored for now (could implement post-filtering if needed)
        search_url = f"ytsearch{max_results}:{query}"
        ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True, 'socket_timeout': 60}

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(search_url, download=False)
                videos = []
                if result and 'entries' in result:
                    for entry in result['entries']:
                        if entry:
                            videos.append({
                                'id': entry.get('id'),
                                'title': entry.get('title', 'Unknown'),
                                'channel': entry.get('uploader', 'Unknown'),
                                'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                            })
                return videos
        except Exception as e:
            raise RuntimeError(f"Search failed: {str(e)}")

    def setup_browser(self):
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        self.driver.scopes = ['.*youtube.*']

    def get_transcript(self, video_id):
        try:
            self.driver.get(f"https://www.youtube.com/watch?v={video_id}")
            sleep(3)
            self.driver.execute_script("window.scrollTo(0, 400);")
            sleep(1)
            try:
                btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "tp-yt-paper-button#expand")))
                btn.click()
                sleep(1)
            except:
                pass
            btn = None
            for sel in ["button[aria-label*='transcript' i]", "ytd-button-renderer button[aria-label*='transcript' i]"]:
                try:
                    elems = self.driver.find_elements(By.CSS_SELECTOR, sel)
                    if elems:
                        btn = elems[0]
                        break
                except:
                    continue
            if not btn:
                return None
            self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            sleep(0.5)
            self.driver.execute_script("arguments[0].click();", btn)
            sleep(2)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-transcript-segment-renderer")))
            segs = self.driver.find_elements(By.CSS_SELECTOR, "ytd-transcript-segment-renderer .segment-text")
            if not segs:
                return None
            return ' '.join([s.text.strip() for s in segs if s.text.strip()]).strip()
        except:
            return None

    def save_transcript(self, video, transcript):
        fname = f"{self.sanitize_filename(video['title'])}_{self.sanitize_filename(video['channel'])}_{datetime.now().strftime('%Y-%m-%d')}.md"
        text = re.sub(r'\s+', ' ', transcript).strip()
        sentences = re.split(r'(?<=[.!?])\s+', text)
        paras, curr = [], []
        for s in sentences:
            if s.strip():
                curr.append(s)
                if len(curr) >= 5:
                    paras.append(' '.join(curr))
                    curr = []
        if curr:
            paras.append(' '.join(curr))

        content = f"""# {video['title']}

## Video Information
- **Channel**: {video['channel']}
- **URL**: {video['url']}
- **Scraped**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Transcript

{chr(10).join([p for p in paras])}
"""
        with open(os.path.join(self.output_dir, fname), 'w', encoding='utf-8') as f:
            f.write(content)
        return fname

    def scrape(self, query, max_results=10, filters=None, output_dir=None):
        if output_dir:
            self.output_dir = output_dir
            Path(self.output_dir).mkdir(exist_ok=True)

        from filters import build_filter_string
        filter_str = build_filter_string(filters) if filters else ""

        self._log(f"Searching: {query}")
        videos = self.search_videos(query, max_results, filter_str)
        self._log(f"Found {len(videos)} videos")

        if not videos:
            return {"saved": 0, "skipped": 0, "files": []}

        self.setup_browser()
        saved, skipped, files = 0, [], []

        try:
            for i, vid in enumerate(videos, 1):
                title = vid['title'].encode('ascii', 'ignore').decode('ascii')
                self._log(f"[{i}/{len(videos)}] {title}")

                trans = self.get_transcript(vid['id'])
                if trans:
                    fn = self.save_transcript(vid, trans)
                    files.append(os.path.join(self.output_dir, fn))
                    self._log(f"✓ Saved")
                    saved += 1
                else:
                    self._log("✗ No transcript")
                    skipped.append(vid)

                if i < len(videos):
                    sleep(3)
        finally:
            if self.driver:
                self.driver.quit()

        return {"saved": saved, "skipped": len(skipped), "files": files}
