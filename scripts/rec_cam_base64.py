import serial
import base64
import cv2
import numpy as np
import time

last_time = time.time()
fps_log = []

PORTA = '/dev/ttyUSB0'
BAUD = 921600

try:
    ser = serial.Serial(PORTA, BAUD, timeout=1)
    # Protection against undesirable reset
    ser.dtr = False
    ser.rts = False
    ser.reset_input_buffer()
    
    print("Waiting image... Press 'q' to quit.")
    with open("latency_log.txt", "a") as f:
        while True:
            if ser.in_waiting > 0:
                linha = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if linha.startswith("IMG:"):
                    base64_str = linha[4:] # Removes IMG prefix"
                    
                    try:
                        img_data = base64.b64decode(base64_str)
                        nparr = np.frombuffer(img_data, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        
                        if frame is not None:
                            cv2.imshow('ESP-CAM Serial', frame)
                            current_time = time.time()
                            dt = current_time - last_time
                            fps = 1 / dt
                            last_time = current_time
                            print(f"FPS: {fps:.2f} | Estimated Latency: {dt*1000:.0f}ms")
                            f.write(f"{time.time()},{dt}\n")
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break
                    except:
                        continue

except Exception as e:
    print(f"Error: {e}")
finally:
    cv2.destroyAllWindows()
    f.close()
    if 'ser' in locals(): ser.close()