import serial
import cv2
import numpy as np
import struct
import time

# --- CONFIGURATION ---
SERIAL_PORT = '/dev/ttyUSB0' 
BAUD_RATE = 921600

def main():
    print(f"Connecting to {SERIAL_PORT} at {BAUD_RATE}...")
    try:
        # Initializing Serial with DTR/RTS disabled to prevent reset loop
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        ser.dtr = False
        ser.rts = False
        ser.reset_input_buffer()
        print("Connection established. Waiting for Raw Binary Stream...")
    except Exception as e:
        print(f"Connection Error: {e}")
        return

    last_time = time.time()
    
    try:
        with open("latency_log.txt", "a") as f:
            while True:
                # 1. Sync: Look for Magic Header 0xAA 0xBB
                if ser.read() == b'\xAA':
                    if ser.read() == b'\xBB':
                        
                        # 2. Read Payload Size (4 bytes)
                        size_data = ser.read(4)
                        if len(size_data) == 4:
                            img_size = struct.unpack('<I', size_data)[0]
                            
                            # 3. Read Raw JPEG Bytes
                            img_data = b''
                            while len(img_data) < img_size:
                                chunk = ser.read(img_size - len(img_data))
                                if not chunk: break
                                img_data += chunk
                            
                            if len(img_data) == img_size:
                                # 4. Decode and Metrics
                                nparr = np.frombuffer(img_data, np.uint8)
                                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                                
                                if frame is not None:
                                    # Calculate FPS
                                    current_time = time.time()
                                    dt = current_time - last_time
                                    fps = 1 / dt
                                    last_time = current_time
                                    
                                    # Visual Overlay
                                    cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), 
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                                    cv2.imshow('Raw Binary Stream', frame)
                                    print(f"FPS: {fps:.2f} | Estimated Latency: {dt*1000:.0f}ms")
                                    f.write(f"{time.time()},{dt}\n")
                                    
                                    if cv2.waitKey(1) & 0xFF == ord('q'):
                                        break
                                else:
                                    print("Warning: Frame decode failed")
                                    
    except KeyboardInterrupt:
        print("\nStopping Diagnostic...")
    finally:
        f.close()
        ser.close()
        cv2.destroyAllWindows()
        print("Resources released.")

if __name__ == "__main__":
    main()