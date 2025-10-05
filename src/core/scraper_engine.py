#!/usr/bin/env python3
"""YouTube Transcript Scraper - Core Engine"""
import os, re, sys, json, yt_dlp
from time import sleep
from datetime import datetime, timedelta
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
        self.output_dir, self.callback, self.driver = output_dir, callback, None
        Path(self.output_dir).mkdir(exist_ok=True)

    def _log(self, msg):
        (self.callback(msg) if self.callback else print(msg))

    def sanitize_filename(self, text, max_len=80):
        return (
            re.sub(r"\s+", "_", re.sub(r'[\\/*?:"<>|]', "", re.sub(r"[\r\n]+", " ", text).strip()))[
                :max_len
            ]
            or "untitled"
        )

    def search_videos(self, query, max_results=10, filters=None):
        ydl_opts = {"quiet": True, "no_warnings": True, "extract_flat": True, "socket_timeout": 60}
        if filters and filters.get("sort_by") and filters["sort_by"] != "relevance":
            ydl_opts["playlistsort"] = filters["sort_by"]
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result, videos = (
                    ydl.extract_info(f"ytsearch{max_results*3}:{query}", download=False),
                    [],
                )
                cutoff_date = (
                    datetime.now() - timedelta(days=filters["upload_date"])
                    if filters and filters.get("upload_date") != "any"
                    else None
                )
                if result and "entries" in result:
                    for entry in result["entries"]:
                        if (
                            entry
                            and len(videos) < max_results
                            and not (
                                cutoff_date
                                and entry.get("upload_date")
                                and datetime.strptime(entry["upload_date"], "%Y%m%d") < cutoff_date
                            )
                        ):
                            videos.append(
                                {
                                    "id": entry.get("id"),
                                    "title": entry.get("title", "Unknown"),
                                    "channel": entry.get("uploader", "Unknown"),
                                    "url": entry.get("url")
                                    or f"https://www.youtube.com/watch?v={entry.get('id')}",
                                }
                            )
                return videos
        except Exception as e:
            raise RuntimeError(f"Search failed: {str(e)}")

    def setup_browser(self):
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=opts
        )
        self.driver.scopes = [".*youtube.*"]

    def get_transcript(self, video_id):
        try:
            self.driver.get(f"https://www.youtube.com/watch?v={video_id}")
            sleep(3)
            self.driver.execute_script("window.scrollTo(0, 400);")
            sleep(1)
            try:
                btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "tp-yt-paper-button#expand"))
                )
                btn.click()
                sleep(1)
            except:
                pass
            btn = None
            for sel in [
                "button[aria-label*='transcript' i]",
                "ytd-button-renderer button[aria-label*='transcript' i]",
            ]:
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
                EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-transcript-segment-renderer"))
            )

            # Find transcript container and scroll to load all segments
            try:
                container = self.driver.find_element(
                    By.CSS_SELECTOR, "ytd-engagement-panel-section-list-renderer[target-id='engagement-panel-searchable-transcript']"
                )
                # Scroll to bottom of transcript panel to force-load all segments
                last_height = 0
                max_scrolls = 20  # Prevent infinite loop
                scroll_count = 0
                while scroll_count < max_scrolls:
                    self.driver.execute_script(
                        "arguments[0].scrollTo(0, arguments[0].scrollHeight);",
                        container
                    )
                    sleep(0.5)
                    new_height = self.driver.execute_script(
                        "return arguments[0].scrollHeight", container
                    )
                    if new_height == last_height:
                        break  # No more content to load
                    last_height = new_height
                    scroll_count += 1
            except:
                # Fallback if container not found - use old method
                pass

            # Now grab ALL segments (fully loaded)
            segs = self.driver.find_elements(
                By.CSS_SELECTOR, "ytd-transcript-segment-renderer .segment-text"
            )
            if not segs:
                return None
            return " ".join([s.text.strip() for s in segs if s.text.strip()]).strip()
        except:
            return None

    def save_transcript(self, video, transcript):
        fname = f"{self.sanitize_filename(video['title'])}_{self.sanitize_filename(video['channel'])}_{datetime.now().strftime('%Y-%m-%d')}.md"
        paras, curr = [], []
        for s in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", transcript).strip()):
            if s.strip():
                curr.append(s)
                if len(curr) >= 5:
                    paras.append(" ".join(curr))
                    curr = []
        if curr:
            paras.append(" ".join(curr))
        content = f"# {video['title']}\n\n## Video Information\n- **Channel**: {video['channel']}\n- **URL**: {video['url']}\n- **Scraped**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n## Transcript\n\n{chr(10).join(paras)}\n"
        with open(os.path.join(self.output_dir, fname), "w", encoding="utf-8") as f:
            f.write(content)
        return fname

    def scrape(self, query, max_results=10, filters=None, output_dir=None):
        if output_dir:
            self.output_dir = output_dir
            Path(self.output_dir).mkdir(exist_ok=True)
        self._log(f"Searching for: {query}")
        videos = self.search_videos(query, max_results, filters)
        self._log(f"✓ Found {len(videos)} relevant videos")
        if not videos:
            return {"saved": 0, "skipped": 0, "files": []}
        self.setup_browser()
        saved, skipped, files = 0, [], []
        try:
            for i, vid in enumerate(videos, 1):
                title = vid["title"].encode("ascii", "ignore").decode("ascii")
                self._log(f"[{i}/{len(videos)}] {title}")
                trans = self.get_transcript(vid["id"])
                if trans:
                    fn = self.save_transcript(vid, trans)
                    files.append(os.path.join(self.output_dir, fn))
                    self._log(f"✓ Extracted successfully")
                    saved += 1
                else:
                    self._log("⊘ Skipped (no transcript available)")
                    skipped.append(vid)
                if i < len(videos):
                    sleep(3)
        finally:
            if self.driver:
                self.driver.quit()
        return {"saved": saved, "skipped": len(skipped), "files": files}
