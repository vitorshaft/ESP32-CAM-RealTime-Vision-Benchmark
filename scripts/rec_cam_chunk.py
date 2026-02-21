import serial
import cv2
import numpy as np
import struct
import time

# --- CONFIGURATION ---
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 921600
LOG_FILE = "chunking_latency_log.txt"

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        ser.dtr = False
        ser.rts = False
        ser.reset_input_buffer()
        print(f"Logging data to {LOG_FILE}...")
    except Exception as e:
        print(f"Error: {e}")
        return

    last_time = time.time()

    while True:
        if ser.read() == b'\xCC': # Frame Start
            start_capture = time.time()
            
            # Read metadata
            total_size = struct.unpack('<I', ser.read(4))[0]
            num_chunks = struct.unpack('<H', ser.read(2))[0]
            
            full_image = b''
            valid_frame = True

            for _ in range(num_chunks):
                if ser.read() == b'\xDD': # Chunk Start
                    chunk_id = struct.unpack('<H', ser.read(2))[0]
                    chunk_len = struct.unpack('<H', ser.read(2))[0]
                    payload = ser.read(chunk_len)
                    checksum = ser.read(1)[0]
                    
                    # Verify Checksum
                    calc_checksum = 0
                    for b in payload: calc_checksum ^= b
                    
                    if calc_checksum == checksum:
                        full_image += payload
                    else:
                        valid_frame = False
                        break

            if valid_frame and len(full_image) == total_size:
                nparr = np.frombuffer(full_image, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is not None:
                    # Time and Metrics calculation
                    current_time = time.time()
                    elapsed = current_time - last_time
                    last_time = current_time
                    
                    # Log Data (Standardized Format: timestamp,latency_delta)
                    with open(LOG_FILE, "a") as f:
                        f.write(f"{current_time},{elapsed}\n")

                    cv2.putText(frame, f"CHUNKING MODE - FPS: {1/elapsed:.2f}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                    cv2.imshow('ESP-CAM - Packetized', frame)
                    
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    ser.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()