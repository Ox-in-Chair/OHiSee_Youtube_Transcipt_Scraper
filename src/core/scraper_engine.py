#!/usr/bin/env python3
"""YouTube Transcript Scraper - Core Engine"""
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

import yt_dlp
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
        if self.callback:
            self.callback(msg)
        else:
            print(msg)

    def sanitize_filename(self, text, max_len=80):
        return (
            re.sub(r"\s+", "_", re.sub(r'[\\/*?:"<>|]', "", re.sub(r"[\r\n]+", " ", text).strip()))[:max_len]
            or "untitled"
        )

    def _attempt_search(self, query, max_results, filters):
        """
        Single search attempt (extracted for reusability across tiers).

        Args:
            query: YouTube search query string
            max_results: Maximum number of results to return
            filters: Dict with 'upload_date' (int days or 'any') and 'sort_by'

        Returns:
            List of video dicts with keys: id, title, channel, url
        """
        ydl_opts = {"quiet": True, "no_warnings": True, "extract_flat": True, "socket_timeout": 60}
        if filters and filters.get("sort_by") and filters["sort_by"] != "relevance":
            ydl_opts["playlistsort"] = filters["sort_by"]
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(f"ytsearch{max_results*3}:{query}", download=False)
                videos = []
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
                                    "url": entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}",
                                }
                            )
                return videos
        except Exception as e:
            self._log(f"⚠ Search attempt failed: {str(e)}")
            return []

    def search_videos(self, query, max_results=10, filters=None, original_query=None):
        """
        Multi-tier search strategy to prevent zero-result failures.

        Tier 1: Use optimized query with all filters
        Tier 2: Fallback to original (unoptimized) query if Tier 1 returns few results
        Tier 3: Relax upload_date filter (expand time window)
        Tier 4: Try GPT-4 synonym expansion (if API key configured)

        Args:
            query: Optimized search query (from GPT-4 or user input)
            max_results: Target number of results
            filters: Dict with 'upload_date' and 'sort_by'
            original_query: Original user query before AI optimization (optional)

        Returns:
            List of video dicts, using best tier that meets/exceeds max_results
        """
        # TIER 1: Optimized query with all filters
        self._log(f"[Tier 1] Searching with optimized query: '{query}'")
        results = self._attempt_search(query, max_results, filters)

        if len(results) >= max_results:
            self._log(f"✓ Tier 1 successful: {len(results)} results")
            return results

        # TIER 2: Fallback to original unoptimized query
        if original_query and original_query != query:
            self._log(f"⊘ Tier 1 returned {len(results)} results (below target of {max_results})")
            self._log(f"[Tier 2] Trying original query: '{original_query}'")
            results_tier2 = self._attempt_search(original_query, max_results, filters)

            if len(results_tier2) > len(results):
                self._log(f"✓ Tier 2 successful: {len(results_tier2)} results (better than Tier 1)")
                return results_tier2

        # TIER 3: Relax upload_date filter (if currently restricted)
        if filters and filters.get("upload_date") != "any":
            self._log(f"⊘ Tier 2 returned {len(results)} results")
            self._log(f"[Tier 3] Relaxing upload_date filter (was {filters['upload_date']} days)")
            relaxed_filters = {**filters, "upload_date": "any"}
            results_tier3 = self._attempt_search(query, max_results, relaxed_filters)

            if len(results_tier3) > len(results):
                self._log(f"✓ Tier 3 successful: {len(results_tier3)} results")
                return results_tier3

        # TIER 4: GPT-4 synonym expansion (if API key configured)
        broader_query = self._get_synonym_expansion(query)
        if broader_query and broader_query != query:
            self._log(f"⊘ Tier 3 returned {len(results)} results")
            self._log(f"[Tier 4] Trying broader query: '{broader_query}'")
            results_tier4 = self._attempt_search(broader_query, max_results, {"upload_date": "any"})

            if len(results_tier4) > len(results):
                self._log(f"✓ Tier 4 successful: {len(results_tier4)} results")
                return results_tier4

        # Return best attempt (even if below target or 0 results)
        self._log(f"⚠ All tiers exhausted. Returning {len(results)} results.")
        return results

    def _get_synonym_expansion(self, query):
        """
        Ask GPT-4 to suggest a broader synonym variation.
        Only called if Config has API key configured.

        Args:
            query: Original search query that returned few results

        Returns:
            Broader query string, or None if API key unavailable or expansion failed
        """
        try:
            from core.search_optimizer import get_synonym_expansion
            from utils.config import Config

            config = Config()
            api_key = config.load_api_key()

            if not api_key:
                return None

            return get_synonym_expansion(query, api_key)
        except Exception:
            return None

    def setup_browser(self):
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
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
            except Exception:
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
                except Exception:
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
                    By.CSS_SELECTOR,
                    "ytd-engagement-panel-section-list-renderer[target-id='engagement-panel-searchable-transcript']",
                )
                # Scroll to bottom of transcript panel to force-load all segments
                last_height = 0
                max_scrolls = 20  # Prevent infinite loop
                scroll_count = 0
                while scroll_count < max_scrolls:
                    self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", container)
                    sleep(0.5)
                    new_height = self.driver.execute_script("return arguments[0].scrollHeight", container)
                    if new_height == last_height:
                        break  # No more content to load
                    last_height = new_height
                    scroll_count += 1
            except Exception:
                # Fallback if container not found - use old method
                pass

            # Now grab ALL segments (fully loaded)
            segs = self.driver.find_elements(By.CSS_SELECTOR, "ytd-transcript-segment-renderer .segment-text")
            if not segs:
                return None
            return " ".join([s.text.strip() for s in segs if s.text.strip()]).strip()
        except Exception:
            return None

    def save_transcript(self, video, transcript):
        title = self.sanitize_filename(video["title"])
        channel = self.sanitize_filename(video["channel"])
        date_str = datetime.now().strftime("%Y-%m-%d")
        fname = f"{title}_{channel}_{date_str}.md"
        paras, curr = [], []
        for s in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", transcript).strip()):
            if s.strip():
                curr.append(s)
                if len(curr) >= 5:
                    paras.append(" ".join(curr))
                    curr = []
        if curr:
            paras.append(" ".join(curr))

        # Build markdown content
        scraped_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        content = (
            f"# {video['title']}\n\n"
            f"## Video Information\n"
            f"- **Channel**: {video['channel']}\n"
            f"- **URL**: {video['url']}\n"
            f"- **Scraped**: {scraped_time}\n\n"
            f"## Transcript\n\n"
            f"{chr(10).join(paras)}\n"
        )

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
                    self._log("✓ Extracted successfully")
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
