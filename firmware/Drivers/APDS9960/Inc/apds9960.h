/*
 * apds9960.h
 *
 *  Created on: Aug 20, 2026
 *      Author: Dora_
 */

#ifndef APDS9960_INC_APDS9960_H_
#define APDS9960_INC_APDS9960_H_

#include <stdint.h>
#include "stm32f4xx_hal.h"


typedef struct
{
    uint16_t clearRaw;
    uint16_t redRaw;
    uint16_t greenRaw;
    uint16_t blueRaw;

    uint8_t proximityRaw;

} APDS9960Reading;

HAL_StatusTypeDef APDS9960Sensor_Init(I2C_HandleTypeDef *i2cHandle);

HAL_StatusTypeDef APDS9960Sensor_Read( APDS9960Reading *reading);


#endif /* APDS9960_INC_APDS9960_H_ */
