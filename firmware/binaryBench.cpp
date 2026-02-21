#include "esp_camera.h"
#include "Arduino.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

/** VISION BENCHMARK (RAW BINARY)
 * Method: Direct byte stream with 0xAA 0xBB header
 * Goal: Achieve maximum efficiency and minimum jitter
 */

// Camera Pins (AI Thinker Model)
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

unsigned long startTime;
unsigned long processTime;
uint32_t frameCount = 0;

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Disable brownout resets
  Serial.begin(921600);
  
  pinMode(4, OUTPUT);
  digitalWrite(4, LOW); // LED OFF

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM; config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM; config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM; config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM; config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM; config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM; config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM; config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM; config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QVGA;
  config.jpeg_quality = 12;
  config.fb_count = 2;

  if (esp_camera_init(&config) != ESP_OK) return;
}

void loop() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) return;

  // --- CPU BENCHMARK START ---
  startTime = micros();
  uint32_t length = fb->len;
  uint8_t* data = fb->buf;
  processTime = micros() - startTime;
  // --- CPU BENCHMARK END ---

  // Protocol: [HEADER 2b][SIZE 4b][DATA]
  Serial.write(0xAA);
  Serial.write(0xBB);
  Serial.write((uint8_t*)&length, 4);
  Serial.write(data, length);

  frameCount++;
  if (frameCount % 100 == 0) {
    Serial.print("\n[CPU_STATS] Binary Processing: ");
    Serial.print(processTime);
    Serial.println(" us\n");
  }

  esp_camera_fb_return(fb);
  delay(10); 
}