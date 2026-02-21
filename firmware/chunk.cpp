#include <Arduino.h>
#include "esp_camera.h"

// Camera Pins (AI Thinker)
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

#define CHUNK_SIZE 512
#define UART_BAUD 921600

uint32_t frame_count = 0;

void setup() {
  Serial.begin(UART_BAUD);
  pinMode(4, OUTPUT);
  digitalWrite(4, LOW); // Flash OFF

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
  config.fb_count = 1;

  esp_camera_init(&config);
}

void loop() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) return;

  uint32_t total_len = fb->len;
  uint16_t num_chunks = (total_len + CHUNK_SIZE - 1) / CHUNK_SIZE;

  // Frame Start Indicator
  Serial.write(0xCC); // Start of Packetized Frame
  Serial.write((uint8_t*)&total_len, 4);
  Serial.write((uint8_t*)&num_chunks, 2);

  for (uint16_t i = 0; i < num_chunks; i++) {
    uint16_t current_chunk_size = (i == num_chunks - 1) ? (total_len % CHUNK_SIZE) : CHUNK_SIZE;
    if (current_chunk_size == 0) current_chunk_size = CHUNK_SIZE;

    // Chunk Header
    Serial.write(0xDD); // Start of Chunk
    Serial.write((uint8_t*)&i, 2); // Chunk ID
    Serial.write((uint8_t*)&current_chunk_size, 2);
    
    // Chunk Data
    uint8_t* data_ptr = fb->buf + (i * CHUNK_SIZE);
    Serial.write(data_ptr, current_chunk_size);
    
    // Simple Checksum
    uint8_t checksum = 0;
    for(uint16_t j=0; j<current_chunk_size; j++) checksum ^= data_ptr[j];
    Serial.write(checksum);
  }

  esp_camera_fb_return(fb);
  frame_count++;
  delay(20);
}