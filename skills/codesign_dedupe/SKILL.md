---
description: Identifies duplicate icon Unicode values across all project folders in Tencent Codesign using Playwright automation.
---

# CodeDesign Icon Unicode Dedupe Tool

This skill automates the process of finding duplicate icon Unicodes within a Codesign "资源库" (Resource Library). It uses Playwright to open a browser, allows you to log in, and then systematically navigates through every icon folder card, scraping names and Unicode values to find duplicates.

## Prerequisites

This skill requires Python and the `playwright` library.

Before running the script for the first time, you must install the Playwright browsers:

```bash
cd /Users/mawangxizi/Desktop/CodeDesign_Tool/skills/codesign_dedupe/
source venv/bin/activate
playwright install chromium
```

*(Note: The virtual environment `venv` is expected to be created and dependencies installed via `pip install -r requirements.txt` prior to this step).*

## Usage Instructions

To run the deduplication check:

1.  Open your terminal.
2.  Navigate to the skill directory and activate the virtual environment:
    ```bash
    cd /Users/mawangxizi/Desktop/CodeDesign_Tool/skills/codesign_dedupe/
    source venv/bin/activate
    ```
3.  Execute the Python script:
    ```bash
    python scripts/dedupe.py
    ```
4.  **Important:** A browser window will open. The script will pause in the terminal.
5.  In the browser, manually log in to Codesign and navigate to your desired "资源库" (Resource Library).
6.  Ensure the "图标" (Icon) tab is active and you can see the folder cards.
7.  Return to your terminal and press `Enter`.
8.  The script will now take control, clicking into each folder, scraping the data, and returning to the list. Do not interact with the browser while it is scanning.
9.  Once finished, the terminal will print a report of any duplicate Unicodes found across all folders.
