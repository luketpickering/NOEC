
#include <Arduino_LSM9DS1.h>

#include "proto/noec_protocol.h"

float x, y, z;
float x_avg, y_avg, z_avg;

int i;

// the setup function runs once when you press reset or power the board
void setup() {

  Serial.begin(9600);
  while (!Serial)
    ;

  if (!IMU.begin()) {
    while (1)
      ;
  }

  i = 0;
  x_avg = 0;
  y_avg = 0;
  z_avg = 0;

  // initialize digital pin LED_BUILTIN as an output.
}

// the loop function runs over and over again forever
void loop() {

  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);
    x_avg += x * 2.55;
    y_avg += y * 2.55;
    z_avg += z * 2.55;
    i++;

    if (i == 100) {
      i = 0;

      noec::msg::clear_values();
      noec::msg::add_values(0, x_avg);
      noec::msg::add_values(1, y_avg);
      noec::msg::add_values(2, z_avg);

      auto &buf = noec::msg::serialize();

#ifdef MSG_HEX
      for (int i = 0; i < buf.get_size(); ++i) {
        Serial.print(buf.get_data()[i], HEX);
      }
      Serial.print("\n");
#else
      Serial.write(buf.get_data(), buf.get_size());
#endif

      x_avg = 0;
      y_avg = 0;
      z_avg = 0;
    }
  }
}
