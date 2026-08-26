/*
 * bme688_sensor.h
 *
 *  Created on: Aug 12, 2026
 *      Author: Dora_
 */

#ifndef INC_BME688_SENSOR_H_
#define INC_BME688_SENSOR_H_

#include "stm32f4xx_hal.h"


typedef struct
{
    float temperatureC;
    float humidityPercent;
    float pressureHpa;
    uint32_t gasResistanceOhm;

    uint8_t gasValid;
    uint8_t heaterStable;
} BME688Reading;


HAL_StatusTypeDef BME688Sensor_Init(I2C_HandleTypeDef *i2cHandle);
HAL_StatusTypeDef BME688Sensor_Read(BME688Reading *reading);



#endif /* INC_BME688_SENSOR_H_ */
