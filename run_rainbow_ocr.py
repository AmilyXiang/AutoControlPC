#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoControlPC - Rainbow启动脚本(带OCR识别)
功能: Win+R -> rainbow -> Enter -> 移动鼠标 -> 点击 -> 输入text -> OCR识别Cui Ji -> 点击
"""

import auto_controller as ac
import time
from PIL import ImageGrab
import cv2
import numpy as np

# 全局OCR读取器
_ocr_reader = None


def init_ocr():
    """初始化OCR读取器(仅初始化一次)"""
    global _ocr_reader
    if _ocr_reader is None:
        print("  Initializing OCR engine...")
        try:
            import easyocr
            _ocr_reader = easyocr.Reader(['en'], gpu=False)
            print("  [OK] OCR engine initialized")
        except Exception as e:
            print(f"  [ERROR] OCR init failed: {e}")
            return False
    return True


def find_text_position(target_text, screenshot=None):
    """
    Find target text position using EasyOCR
    Tries multiple matching strategies:
    1. Exact case-sensitive match
    2. Case-insensitive match
    3. Partial word match (for text broken across lines)
    """
    try:
        # Initialize OCR if not yet done
        if not init_ocr():
            return None
        
        # Get screenshot if not provided
        if screenshot is None:
            print("  Capturing screenshot...")
            screenshot = ImageGrab.grab()
        
        # Convert to numpy array
        img_array = np.array(screenshot)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Perform OCR recognition
        print("  Recognizing text...")
        results = _ocr_reader.readtext(img_bgr)
        
        print(f"  Found {len(results)} text areas")
        
        target_lower = target_text.lower()
        target_words = target_text.split()  # e.g., ['Cui', 'Ji']
        
        candidates = []  # Store potential matches with scores
        
        for (bbox, text, confidence) in results:
            text_stripped = text.strip()
            text_lower = text_stripped.lower()
            
            # Strategy 1: Exact case-sensitive match
            if target_text in text_stripped or text_stripped in target_text:
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                center_x = int(sum(x_coords) / 4)
                center_y = int(sum(y_coords) / 4)
                print(f"  [OK] Found exact match '{text_stripped}' at ({center_x}, {center_y})")
                return (center_x, center_y)
            
            # Strategy 2: Case-insensitive match
            if target_lower in text_lower or text_lower in target_lower:
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                center_x = int(sum(x_coords) / 4)
                center_y = int(sum(y_coords) / 4)
                # Store as candidate
                candidates.append({
                    'text': text_stripped,
                    'confidence': confidence,
                    'x': center_x,
                    'y': center_y,
                    'score': 1.0  # Full match
                })
            
            # Strategy 3: Check if all target words appear in this text
            elif all(word.lower() in text_lower for word in target_words):
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                center_x = int(sum(x_coords) / 4)
                center_y = int(sum(y_coords) / 4)
                candidates.append({
                    'text': text_stripped,
                    'confidence': confidence,
                    'x': center_x,
                    'y': center_y,
                    'score': 0.8
                })
        
        # Return best candidate if found
        if candidates:
            best = max(candidates, key=lambda x: (x['score'], x['confidence']))
            print(f"  [OK] Found '{best['text']}' (confidence: {best['confidence']:.2f}) at ({best['x']}, {best['y']})")
            return (best['x'], best['y'])
        
        print(f"  [NOTFOUND] Text '{target_text}' not found")
        return None
    
    except Exception as e:
        print(f"  [ERROR] OCR error: {e}")
        return None


def main():
    """Main function - Execute Rainbow app startup"""
    
    print("="*70)
    print("  Rainbow App Launcher with OCR Recognition")
    print("="*70)
    print()
    
    print("Preparing to start Rainbow app...")
    print("Will execute the following steps:")
    print("  1. Press Win key (open run dialog)")
    print("  2. Type 'rainbow'")
    print("  3. Press Enter (start app)")
    print("  4. Move mouse to position (100, 80)")
    print("  5. Click mouse")
    print("  6. Type 'cui ji'")
    print("  7. Use OCR to find 'Cui Ji' coordinates")
    print("  8. Move to 'Cui Ji' and click")
    print("  9. Wait for interface update")
    print("  10. Find 'Call' button and click")
    print("  11. Wait for Call menu to appear")
    print("  12. Find 'Audio' button and click")
    print()
    
    # Wait for user to prepare
    print("[READY] Starting in 2 seconds...")
    time.sleep(2)
    
    try:
        # Step 1: Press Win key
        print("\n[Step 1] Pressing Win key...")
        ac.tap_key('win')
        time.sleep(0.5)
        print("[OK] Win key pressed, run dialog should be open")
        
        # Wait for run dialog to fully open
        time.sleep(0.5)
        
        # Step 2: Type rainbow
        print("\n[Step 2] Typing 'rainbow'...")
        ac.type_text('rainbow', interval=0.1)
        time.sleep(0.3)
        print("[OK] 'rainbow' typed")
        
        # Step 3: Press Enter
        print("\n[Step 3] Pressing Enter...")
        ac.tap_key('enter')
        time.sleep(1)
        print("[OK] Enter pressed, app is starting")
        
        # Wait for app to start
        time.sleep(1)
        
        # Step 4: Move mouse to position (100, 80)
        print("\n[Step 4] Moving mouse to position (100, 80)...")
        ac.move_mouse(100, 80, duration=0.5)
        time.sleep(0.3)
        print("[OK] Mouse moved to (100, 80)")
        
        # Step 5: Click
        print("\n[Step 5] Clicking mouse...")
        ac.left_click()
        time.sleep(0.3)
        print("[OK] Mouse clicked")
        
        # Step 6: Type 'cui ji'
        print("\n[Step 6] Typing 'cui ji'...")
        ac.type_text('cui ji', interval=0.1)
        time.sleep(0.3)
        print("[OK] 'cui ji' typed")
        
        # Wait for text to display
        time.sleep(1)
        
        # Step 7: OCR recognition to find 'Cui Ji'
        print("\n[Step 7] Using OCR to find 'Cui Ji' coordinates...")
        screenshot = ImageGrab.grab()
        
        # Debug: Save screenshot for inspection
        screenshot.save("last_rainbow_screenshot.png")
        print("  [DEBUG] Screenshot saved to: last_rainbow_screenshot.png")
        
        position = find_text_position('Cui Ji', screenshot)
        
        if position:
            # Step 8: Move to that coordinate and click
            print(f"\n[Step 8] Moving mouse to recognized position {position}...")
            ac.move_mouse(position[0], position[1], duration=0.5)
            time.sleep(0.3)
            print("[OK] Mouse moved")
            
            print("\n[Step 8 cont] Clicking mouse...")
            ac.left_click()
            time.sleep(0.3)
            print("[OK] Mouse clicked")
            
            # Step 9: Wait and take new screenshot after clicking
            print("\n[Step 9] Waiting for interface update after clicking 'Cui Ji'...")
            time.sleep(1)
            
            # Step 10: Find and click "Call" button
            print("\n[Step 10] Using OCR to find and click 'Call' button...")
            screenshot = ImageGrab.grab()
            screenshot.save("after_cui_ji_click.png")
            print("  [DEBUG] Screenshot saved to: after_cui_ji_click.png")
            
            call_position = find_text_position('Call', screenshot)
            
            if call_position:
                print(f"\n  Moving mouse to Call button at {call_position}...")
                ac.move_mouse(call_position[0], call_position[1], duration=0.5)
                time.sleep(0.3)
                print("[OK] Mouse moved to Call button")
                
                print("\n  Clicking Call button...")
                ac.left_click()
                time.sleep(0.5)
                print("[OK] Call button clicked")
                
                # Step 11: Wait and find Audio button
                print("\n[Step 11] Waiting for Call menu to appear...")
                time.sleep(1)
                
                print("\n[Step 12] Using OCR to find and click 'Audio' button...")
                screenshot = ImageGrab.grab()
                screenshot.save("after_call_click.png")
                print("  [DEBUG] Screenshot saved to: after_call_click.png")
                
                audio_position = find_text_position('Audio', screenshot)
                
                if audio_position:
                    print(f"\n  Moving mouse to Audio button at {audio_position}...")
                    ac.move_mouse(audio_position[0], audio_position[1], duration=0.5)
                    time.sleep(0.3)
                    print("[OK] Mouse moved to Audio button")
                    
                    print("\n  Clicking Audio button...")
                    ac.left_click()
                    time.sleep(0.5)
                    print("[OK] Audio button clicked")
                else:
                    print("\n  [WARNING] 'Audio' button not found")
            else:
                print("\n  [WARNING] 'Call' button not found")
        else:
            print("\n[WARNING] OCR could not find 'Cui Ji', skipping steps 8-10")
        
        print("\n" + "="*70)
        print("SUCCESS - All operations completed!")
        print("="*70)
        print("\nCompleted steps:")
        print("  1. [OK] Pressed Win key")
        print("  2. [OK] Typed 'rainbow'")
        print("  3. [OK] Pressed Enter")
        print("  4. [OK] Moved mouse to (100, 80)")
        print("  5. [OK] Clicked mouse")
        print("  6. [OK] Typed 'cui ji'")
        print("  7. [OK] OCR recognized 'Cui Ji' coordinates")
        if position:
            print(f"  8. [OK] Moved to 'Cui Ji' and clicked {position}")
            print("  9. [OK] Waited for interface update")
            print("  10. [OK] Found and clicked 'Call' button")
        else:
            print("  8-10. [SKIP] Skipped (text not found)")
        print()
        
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Program interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Exception occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
