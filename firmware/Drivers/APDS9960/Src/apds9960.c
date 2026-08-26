/*
 * apds9960.c
 *
 *  Created on: Aug 20, 2026
 *      Author: Dora_
 */

#include "apds9960.h"

#define APDS9960_I2C_ADDRESS_7BIT       0x39U
#define APDS9960_I2C_ADDRESS_HAL     ((uint16_t)(APDS9960_I2C_ADDRESS_7BIT << 1U))

#define APDS9960_I2C_TIMEOUT_MS         100U


/*registers*/
#define APDS9960_EXPECTED_DEVICE_ID     0xABU
#define APDS9960_REGISTER_ID            0x92U
#define APDS9960_REGISTER_ENABLE         0x80U
#define APDS9960_REGISTER_ATIME         0x81U
#define APDS9960_REGISTER_PPULSE        0x8EU
#define APDS9960_REGISTER_CONTROL       0x8FU
#define APDS9960_REGISTER_STATUS        0x93U
#define APDS9960_REGISTER_CDATAL        0x94U
#define APDS9960_REGISTER_PDATA         0x9CU

#define APDS9960_ENABLE_POWER           0x01U
#define APDS9960_ENABLE_COLOR           0x02U
#define APDS9960_ENABLE_PROXIMITY       0x04U

#define APDS9960_ATIME_VALUE            0xDCU
#define APDS9960_PPULSE_VALUE           0x8FU
#define APDS9960_CONTROL_VALUE          0x05U
#define APDS9960_STATUS_COLOR_VALID     0x01U
#define APDS9960_STATUS_PROXIMITY_VALID 0x02U
/* Private variables ---------------------------------------------------------*/

static I2C_HandleTypeDef *apdsI2cHandle = NULL;
static uint8_t isInitialized = 0U;

/* Private function prototypes -----------------------------------------------*/
static HAL_StatusTypeDef APDS9960_WriteRegister(uint8_t registerAddress, uint8_t value);
static HAL_StatusTypeDef APDS9960_ReadRegisters(uint8_t firstRegisterAddress, uint8_t *data, uint16_t dataLength);
static HAL_StatusTypeDef APDS9960_ReadRegister(uint8_t registerAddress, uint8_t *value);



static HAL_StatusTypeDef APDS9960_WriteRegister(uint8_t registerAddress, uint8_t value)
{
	return HAL_I2C_Mem_Write(apdsI2cHandle, APDS9960_I2C_ADDRESS_HAL, registerAddress, I2C_MEMADD_SIZE_8BIT, &value,1U, APDS9960_I2C_TIMEOUT_MS);

}

static HAL_StatusTypeDef APDS9960_ReadRegisters(uint8_t firstRegisterAddress, uint8_t *data, uint16_t dataLength)
{
	return HAL_I2C_Mem_Read(apdsI2cHandle, APDS9960_I2C_ADDRESS_HAL, firstRegisterAddress, I2C_MEMADD_SIZE_8BIT,  data, dataLength, APDS9960_I2C_TIMEOUT_MS);
}

static HAL_StatusTypeDef APDS9960_ReadRegister(uint8_t registerAddress, uint8_t *value)
{
	return APDS9960_ReadRegisters(registerAddress, value, 1U);
}

HAL_StatusTypeDef APDS9960Sensor_Init(I2C_HandleTypeDef *i2cHandle)
{
	HAL_StatusTypeDef halStatus;
	uint8_t deviceId;

	if (i2cHandle == NULL)
	{
	    return HAL_ERROR;
	}

	apdsI2cHandle = i2cHandle;
	isInitialized = 0U;

	//read reg id to be sure that i2c device is really apds
	halStatus = APDS9960_ReadRegister(APDS9960_REGISTER_ID, &deviceId);
	if(halStatus != HAL_OK)
	{
		return halStatus;
	}
	if(deviceId != APDS9960_EXPECTED_DEVICE_ID)
	{
		return HAL_ERROR;
	}

	//disable sensor while configuration
	halStatus = APDS9960_WriteRegister(APDS9960_REGISTER_ENABLE, 0x00U);
	if(halStatus != HAL_OK)
	{
		return halStatus;
	}


	halStatus = APDS9960_WriteRegister(APDS9960_REGISTER_ATIME, APDS9960_ATIME_VALUE);
	if(halStatus != HAL_OK)
	{
		return halStatus;
	}

	halStatus = APDS9960_WriteRegister(APDS9960_REGISTER_PPULSE, APDS9960_PPULSE_VALUE);
	if(halStatus != HAL_OK)
	{
		return halStatus;
	}

	halStatus = APDS9960_WriteRegister(APDS9960_REGISTER_CONTROL, APDS9960_CONTROL_VALUE);
	if(halStatus != HAL_OK)
	{
		return halStatus;
	}

	//enable sensor - als
	halStatus = APDS9960_WriteRegister(APDS9960_REGISTER_ENABLE, 0x01U);
	if(halStatus != HAL_OK)
	{
		return halStatus;
	}
	HAL_Delay(10U); //zbog dijagrama stanja iz ds

	//enable mjerenja napajanje,color i proxy
	halStatus = APDS9960_WriteRegister(APDS9960_REGISTER_ENABLE, APDS9960_ENABLE_POWER | APDS9960_ENABLE_COLOR | APDS9960_ENABLE_PROXIMITY);
    if(halStatus != HAL_OK)
	{
	   return halStatus;
	}

    isInitialized = 1U;

	return HAL_OK;

}

HAL_StatusTypeDef APDS9960Sensor_Read( APDS9960Reading *reading)
{
	HAL_StatusTypeDef halStatus;
	uint8_t sensorStatus;
	uint8_t colorData[8];
	uint8_t proximityData;

	if((isInitialized == 0U) || (reading == NULL))
	{
	   return HAL_ERROR;
	}

	halStatus = APDS9960_ReadRegister(APDS9960_REGISTER_STATUS, &sensorStatus);
	if(halStatus != HAL_OK)
    {
	   return halStatus;
	}

	if((sensorStatus & APDS9960_STATUS_COLOR_VALID) == 0U)
	{
	   return HAL_BUSY;
	}

	if((sensorStatus & APDS9960_STATUS_PROXIMITY_VALID) == 0U)
	{
	   return HAL_BUSY;
	}

	halStatus = APDS9960_ReadRegisters(APDS9960_REGISTER_CDATAL, colorData, sizeof(colorData));
	if(halStatus != HAL_OK)
	{
	   return halStatus;
    }


	halStatus = APDS9960_ReadRegister(APDS9960_REGISTER_PDATA, &proximityData);
	if(halStatus != HAL_OK)
	{
	   return halStatus;
	}


	reading->clearRaw = (uint16_t)colorData[0] | ((uint16_t)colorData[1] << 8U);
	reading->redRaw = (uint16_t)colorData[2] | ((uint16_t)colorData[3] << 8U);
	reading->greenRaw = (uint16_t)colorData[4] | ((uint16_t)colorData[5] << 8U);
	reading->blueRaw = (uint16_t)colorData[6] | ((uint16_t)colorData[7] << 8U);

	reading->proximityRaw = proximityData;

	return HAL_OK;



}
