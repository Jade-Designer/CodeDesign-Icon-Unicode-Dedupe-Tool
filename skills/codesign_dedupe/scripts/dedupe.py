from playwright.sync_api import sync_playwright
import time
from collections import defaultdict

def main():
    with sync_playwright() as p:
        import os
        
        project_root = os.getcwd() # Make path portable for GitHub
        user_data_dir = os.path.join(project_root, "user_data")
        os.makedirs(user_data_dir, exist_ok=True)
        
        print(f"Launching browser with persistent context at: {user_data_dir}")
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            no_viewport=True
        )
        page = context.pages[0] if context.pages else context.new_page()

        # ==========================================
        # 目标图标页面的完整网址
        # 请替换为你项目真实的带资源库的 icon 链接
        TARGET_URL = "https://codesign.qq.com/app/icon/YOUR_PROJECT_ID/detail" 
        # ==========================================

        print(f"Auto-navigating directly to: {TARGET_URL}")
        page.goto(TARGET_URL)

        print("Checking for icon folders or login requirement...")
        try:
            # Check if cards are present already
            page.wait_for_selector('.card__item--container', state='visible', timeout=5000)
            print("Successfully loaded icon library automatically! Beginning scan...")
        except Exception:
            print("\n--- ACTION REQUIRED ---")
            print("Icon cards not detected. You might need to log in.")
            print("Please scan the QR code or log in using the browser window.")
            print("The script is monitoring the page and will automatically resume once you are logged in...")
            
            try:
                # Wait up to 5 minutes (300,000 ms) for the cards to show up after user manually logs in
                page.wait_for_selector('.card__item--container', state='visible', timeout=300000)
                print("\nLogin successful! Icon cards detected. Resuming scan...")
            except Exception:
                print("\n[ERROR] Wait timed out after 5 minutes or cards completely unavailable.")
                context.close()
                return

        icon_data = defaultdict(list)
        
        # --- PHASE 1: Collect Folder Names ---
        print("\n=== PHASE 1: Collecting Folder Names ===")
        # Force a few scrolls to ensure initial lazy load is populated
        for _ in range(4):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            
        cards = page.locator('.card__item--container')
        count = cards.count()
        print(f"Total cards loaded in DOM: {count}")
        
        target_folders = []
        for i in range(count):
            try:
                name_loc = cards.nth(i).locator('.title, h2, h3, .name').first
                if name_loc.count() > 0:
                    folder_name = name_loc.inner_text().strip()
                else:
                    folder_name = ""
            except Exception:
                folder_name = ""
                
            if folder_name and "演示" not in folder_name and "demo" not in folder_name.lower():
                target_folders.append(folder_name)
                
        print(f"Identified {len(target_folders)} valid target folders to scan.\n")
        
        # Save main URL for the loop
        main_url = page.url
        
        # --- PHASE 2: Iterative Extraction ---
        print("=== PHASE 2: Data Extraction ===")
        for idx, folder_name in enumerate(target_folders):
            print(f"Entering Folder [{idx+1}/{len(target_folders)}]: '{folder_name}'")
            
            # Step 1: Guarantee we are on the main list
            try:
                page.goto(main_url)
                page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass
               # Step 2: Scroll until the target folder is visible in DOM
            found = False
            card_to_click = None
            for scroll_attempt in range(10):
                page.wait_for_selector('.card__item--container', state='visible', timeout=5000)
                
                # EXACT MATCH FINDER: Iterate and compare exact inner_text
                current_cards = page.locator('.card__item--container')
                count_now = current_cards.count()
                for c_idx in range(count_now):
                    card = current_cards.nth(c_idx)
                    try:
                        name_el = card.locator('.title, h2, h3, .name').first
                        if name_el.count() > 0 and name_el.inner_text().strip() == folder_name:
                            found = True
                            card_to_click = card
                            break
                    except Exception:
                        pass
                
                if found:
                    break
                    
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)
                
            if not found or card_to_click is None:
                print(f"  [ERROR] Could not locate EXACT folder '{folder_name}' after scrolling. Skipping...")
                continue
                
            # Step 3: Click the target
            try:
                card_to_click.scroll_into_view_if_needed()
                time.sleep(0.5)
                card_to_click.click(timeout=5000)
            except Exception as e:
                print(f"  Standard click failed, trying force click. Error: {e}")
                try:
                    card_to_click.click(force=True, timeout=5000)
                except Exception as e2:
                    print(f"  Force clicking failed. Skipping... Error: {e2}")
                    continue
                    
            # URL CHANGE VALIDATION
            try:
                page.wait_for_function(f"window.location.href !== '{main_url}'", timeout=5000)
            except Exception:
                print(f"  [URL GUARD] URL did not change after click! Clicking again...")
                try:
                    card_to_click.click(force=True, timeout=5000)
                    page.wait_for_function(f"window.location.href !== '{main_url}'", timeout=5000)
                except Exception:
                    print(f"  [CRITICAL] Stuck on main URL for '{folder_name}'. Skipping.")
                    continue
                    
            # Step 4: Extract Icons
            print(f"  Waiting for folder '{folder_name}' to render...")
            
            # MANDATORY 3-second hard wait to let network requests fetch and SPA to render
            page.wait_for_timeout(3000) 
            
            try:
                # EXACT TITLE TEXT MATCH on the page to guarantee we landed on the right folder
                escaped_name = folder_name.replace("'", "\\'")
                page.wait_for_function(
                    f"() => {{ const els = Array.from(document.querySelectorAll('*')); return els.some(el => el.innerText && el.innerText.trim() === '{escaped_name}'); }}", 
                    timeout=5000
                )
                # Wait for the main wrapper to be visible
                page.wait_for_selector('.icons-workspace__list-wrapper', state='visible', timeout=10000)
            except Exception:
                 print("  Note: No wrapper found, or Exact Title failed/timeout. Folder may be empty.")
                 continue

            # Constrain our search ONLY to the specific wrapper container
            wrapper = page.locator('.icons-workspace__list-wrapper').first
            
            icons_found = 0
            first_icon_name = "None (Empty Folder)"
            
            # Stale DOM Guard - verify content has actually updated (Wait up to 10 extra seconds)
            verification_passed = False
            for attempt in range(5):
                icons = wrapper.locator('li.icons-workspace__list-item')
                icons_found = icons.count()
                
                first_icon_name = "None"
                if icons_found > 0:
                    first_name_el = icons.nth(0).locator('p.icons-workspace__list-item-name')
                    # If this locator is not resolved yet, it might throw, so safely try it
                    try:
                        first_icon_name = first_name_el.inner_text().strip() if first_name_el.count() > 0 else "Unknown Name"
                    except Exception:
                        pass
                
                # Check against last folder's first icon to detect stale SPA DOM
                if icons_found > 0 and 'last_first_icon_name' in locals() and first_icon_name == last_first_icon_name:
                    print(f"  [Stale DOM Guard] Still seeing previous icon '{first_icon_name}'. Waiting 2s for DOM refresh...")
                    page.wait_for_timeout(2000)
                    continue
                else:
                    verification_passed = True
                    break
                    
            if not verification_passed:
                print("  [Warning] Never saw content refresh, grabbing what is currently there.")
                
            # Emergency Debug Screenshot Condition for test folder
            if folder_name.lower().strip() == 'test' and icons_found == 8:
                err_path = os.path.join(project_root, "error_test_folder.png")
                page.screenshot(path=err_path)
                print(f"  [DEBUG] Saving screenshot to '{err_path}' because test folder matched the 8-icon error pattern.")

            print(f"  Extracted {icons_found} icons. (First: {first_icon_name})")
            
            # Save it for the next folder's comparison
            if icons_found > 0:
                last_first_icon_name = first_icon_name
            else:
                last_first_icon_name = None

            for j in range(icons_found):
                icon = icons.nth(j)
                name_el = icon.locator('p.icons-workspace__list-item-name')
                uni_el = icon.locator('span.icons-workspace__list-item-label')
                
                name = name_el.inner_text().strip() if name_el.count() > 0 else "Unknown Name"
                uni = uni_el.inner_text().strip() if uni_el.count() > 0 else ""
                
                if uni:
                    icon_data[uni].append({'name': name, 'folder': folder_name})
                
        print("\n=== PHASE 3: Deduplication Results ===\n")
        duplicates_found = False
        report_path = os.path.join(project_root, "duplicate_report.txt")
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("CodeDesign Icon Unicode Dedupe Tool Report\n")
            f.write("==================================\n\n")
            
            for uni, occurrences in icon_data.items():
                if len(occurrences) > 1:
                    duplicates_found = True
                    print(f"DUPLICATE FOUND for Unicode: {uni}")
                    f.write(f"DUPLICATE FOUND for Unicode: {uni}\n")
                    for occ in occurrences:
                        msg = f"  - Icon Name: '{occ['name']}' in Folder: '{occ['folder']}'"
                        print(msg)
                        f.write(msg + "\n")
                    print("-" * 20)
                    f.write("-" * 20 + "\n")
    
            if not duplicates_found:
                print("No duplicates found across the analyzed folders!")
                f.write("No duplicates found across the analyzed folders!\n")
            
        print(f"\nExtraction complete. Detailed report saved to: {report_path}")
        context.close()

if __name__ == "__main__":
    main()
