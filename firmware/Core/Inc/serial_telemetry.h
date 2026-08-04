/*
 * serial_telemetry.h
 *
 *  Created on: Aug 4, 2026
 *      Author: Dora_
 */

#ifndef INC_SERIAL_TELEMETRY_H_
#define INC_SERIAL_TELEMETRY_H_

#include "stm32f4xx_hal.h"

typedef struct
{
	float temperatureC;
	float humidityPercent;
	float pressureHpa;
	uint32_t gasResistanceOhm;

    uint16_t clearRaw;
	uint16_t redRaw;
	uint16_t greenRaw;
	uint16_t blueRaw;
	uint8_t proximityRaw;
}SerialTelemetryReading;

void SerialTelemetry_Init(UART_HandleTypeDef *uartHandle);

HAL_StatusTypeDef SerialTelemetry_Send(const SerialTelemetryReading *reading);

#endif /* INC_SERIAL_TELEMETRY_H_ */
