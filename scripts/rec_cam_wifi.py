import cv2
import urllib.request
import numpy as np
import time

# --- CONFIGURATION ---
# Updated to match the IP shown in your terminal
URL = "http://192.168.0.31/" 
LOG_FILE = "wifi_latency_log.txt"

def main():
    print(f"Connecting to WiFi Stream: {URL}...")
    try:
        stream = urllib.request.urlopen(URL)
        bytes_data = b''
        last_time = time.time()
        print(f"Logging data to {LOG_FILE}...")
    except Exception as e:
        print(f"Connection Failed: {e}")
        return

    while True:
        try:
            chunk = stream.read(1024)
            if not chunk:
                break
            bytes_data += chunk
            
            # Find JPEG markers
            a = bytes_data.find(b'\xff\xd8') # JPEG Start
            b = bytes_data.find(b'\xff\xd9') # JPEG End
            
            # Ensure markers are found and in correct order
            if a != -1 and b != -1:
                if b > a:
                    jpg = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:]
                    
                    if len(jpg) > 0:
                        # Metrics
                        current_time = time.time()
                        elapsed = current_time - last_time
                        last_time = current_time

                        # Log Data (Standardized Format)
                        with open(LOG_FILE, "a") as f:
                            f.write(f"{current_time},{elapsed}\n")

                        # Decode and Display
                        nparr = np.frombuffer(jpg, dtype=np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        
                        if frame is not None:
                            cv2.putText(frame, f"WIFI MODE - FPS: {1/elapsed:.2f}", (10, 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                            cv2.imshow('ESP-CAM - WiFi', frame)
                else:
                    # If end marker found before start marker, drop the garbage
                    bytes_data = bytes_data[b+2:]
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(f"Streaming error: {e}")
            break

    cv2.destroyAllWindows()
    print(f"Finished. Data saved to {LOG_FILE}")

if __name__ == "__main__":
    main()