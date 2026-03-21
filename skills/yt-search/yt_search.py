#!/usr/bin/env python3
"""YouTube Search - otsib videoid ja tagastab metaandmed."""
import subprocess
import json
import sys

def search_youtube(query, count=10):
    """Otsib YouTube'ist ja tagastab metaandmed JSON-ina."""
    cmd = [
        sys.executable, "-m", "yt_dlp",
        f"ytsearch{count}:{query}",
        "--dump-json",
        "--no-download",
        "--flat-playlist"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

    videos = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        try:
            data = json.loads(line)
            videos.append({
                "title": data.get("title", ""),
                "url": data.get("url", data.get("webpage_url", f"https://youtube.com/watch?v={data.get('id', '')}")),
                "channel": data.get("channel", data.get("uploader", "")),
                "views": data.get("view_count", 0),
                "duration": data.get("duration_string", data.get("duration", "")),
                "upload_date": data.get("upload_date", ""),
                "description": (data.get("description", "") or "")[:200]
            })
        except json.JSONDecodeError:
            continue

    return videos

def get_captions(url):
    """Tõmbab video subtiitrid."""
    cmd = [
        sys.executable, "-m", "yt_dlp",
        url,
        "--write-auto-sub",
        "--sub-lang", "en",
        "--skip-download",
        "--sub-format", "txt",
        "-o", "-",
        "--print", "%(subtitles)j"
    ]

    # Simpler approach: get auto-generated subs
    cmd2 = [
        sys.executable, "-m", "yt_dlp",
        url,
        "--no-download",
        "--dump-json"
    ]

    result = subprocess.run(cmd2, capture_output=True, text=True, timeout=120)
    if result.returncode == 0:
        data = json.loads(result.stdout)
        return {
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "duration": data.get("duration_string", ""),
            "url": url
        }
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kasutus: python yt_search.py <otsing> [kogus]")
        sys.exit(1)

    query = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    results = search_youtube(query, count)
    print(json.dumps(results, indent=2, ensure_ascii=False))
