/*
 * serial_telemetry.c
 *
 *  Created on: Aug 4, 2026
 *      Author: Dora_
 */
#include "serial_telemetry.h"


#include <stdio.h>

/* Macro -------------------------------------------------------------*/
#define TELEMETY_BUFFER_SIZE 200U



/* Private variables ---------------------------------------------------------*/
static UART_HandleTypeDef  *uart = NULL;

static char telemetryBuffer[TELEMETY_BUFFER_SIZE];

static uint32_t sequenceNumber = 0U;


/* Private function prototypes -----------------------------------------------*/





void SerialTelemetry_Init(UART_HandleTypeDef *uartHandle)
{
	uart = uartHandle;
	sequenceNumber = 0U;
}

HAL_StatusTypeDef SerialTelemetry_Send(const SerialTelemetryReading *reading)
{

	 if ((uart == NULL) || (reading == NULL))
	 {
	      return HAL_ERROR;
	 }

	 sequenceNumber++;

	 int message_length = snprintf(
			 telemetryBuffer,
			 sizeof(telemetryBuffer),
			 "DATA,%lu,%lu,%.2f,%.2f,%.2f,%lu,%u,%u,%u,%u,%u,%u,%u\r\n",
			 (unsigned long)sequenceNumber,
			 (unsigned long)HAL_GetTick(),
			 (double)reading->temperatureC,
			 (double)reading->humidityPercent,
			 (double)reading->pressureHpa,
			 (unsigned long)reading->gasResistanceOhm,
			 (unsigned int)reading ->gasValid,
			 (unsigned int)reading ->heaterStable,
			 (unsigned int)reading->clearRaw,
			 (unsigned int)reading->redRaw,
			 (unsigned int)reading->greenRaw,
			 (unsigned int)reading->blueRaw,
			 (unsigned int)reading->proximityRaw
	 );

	 if((message_length <= 0) || (message_length >= (int)sizeof(telemetryBuffer)))
	 {
	     return HAL_ERROR;
	 }

	 return HAL_UART_Transmit(uart,(uint8_t *)telemetryBuffer, (uint16_t)message_length, HAL_MAX_DELAY);


}
