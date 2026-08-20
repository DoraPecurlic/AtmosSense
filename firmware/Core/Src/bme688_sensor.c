/*
 * bme688_sensor.c
 *
 *  Created on: Aug 12, 2026
 *      Author: Dora_
 */


#include "bme688_sensor.h"
#include "bme68x.h"

#include <stddef.h>
#include <string.h>

/* Macro -------------------------------------------------------------*/
#define AMBIENT_TEMPERATURE_C  25

#define BME688_I2C_TIMEOUT_MS        100U

//Bosch koristi u svom primejru ove bvrijednosti za force mode
#define BME688_HEATER_TEMPERATURE_C  300U
#define BME688_HEATER_DURATION_MS    100U


/* Structs -------------------------------------------------------------*/

typedef struct
{
    I2C_HandleTypeDef *i2cHandle;
    uint8_t address7Bit;

} BME688Bus;



/* Private variables ---------------------------------------------------------*/
static BME688Bus bus;

static struct bme68x_dev device;
static struct bme68x_conf sensorConfiguration;
static struct bme68x_heatr_conf heaterConfiguration;

static uint8_t isInitialized = 0U;
static int8_t lastDriverResult = BME68X_E_DEV_NOT_FOUND;




/* Private function prototypes -----------------------------------------------*/
static BME68X_INTF_RET_TYPE BME688_Read(uint8_t reg_addr, uint8_t *registerData, uint32_t dataLength, void *intf_ptr);
static BME68X_INTF_RET_TYPE BME688_Write(uint8_t reg_addr, const uint8_t *registerData, uint32_t dataLength,  void *intf_ptr);
static void BME688_DelayMicroseconds(uint32_t period, void *intf_ptr);







static int8_t tryAddress(uint8_t address)
{
	bus.address7Bit = address;

	memset(&device, 0, sizeof(device));

	device.intf = BME68X_I2C_INTF;
	device.intf_ptr = &bus;


	device.amb_temp = AMBIENT_TEMPERATURE_C;

	device.read = BME688_Read;
	device.write = BME688_Write;
	device.delay_us = BME688_DelayMicroseconds;

	return bme68x_init(&device);

}

static BME68X_INTF_RET_TYPE BME688_Read(uint8_t reg_addr, uint8_t *registerData, uint32_t dataLength, void *intf_ptr)
{
	 BME688Bus *selectedBus = (BME688Bus *)intf_ptr;

	 if((selectedBus == NULL) || (selectedBus->i2cHandle == NULL) || (registerData == NULL) || (dataLength == 0U) || (dataLength > UINT16_MAX))
	 {
	      return (BME68X_INTF_RET_TYPE)-1;
	 }
	// HAL_I2C_Mem_Read(I2C_HandleTypeDef *hi2c, uint16_t DevAddress, uint16_t MemAddress, uint16_t MemAddSize, uint8_t *pData, uint16_t Size, uint32_t Timeout)
	 HAL_StatusTypeDef halStatus = HAL_I2C_Mem_Read(selectedBus->i2cHandle,(uint16_t)(selectedBus->address7Bit << 1U), reg_addr, I2C_MEMADD_SIZE_8BIT,registerData, (uint16_t)dataLength, BME688_I2C_TIMEOUT_MS);

	 if(halStatus == HAL_OK){
		 return BME68X_INTF_RET_SUCCESS;
	 }

	 return (BME68X_INTF_RET_TYPE)-1;
}


static BME68X_INTF_RET_TYPE BME688_Write(uint8_t reg_addr, const uint8_t *registerData, uint32_t dataLength,  void *intf_ptr)
{
	BME688Bus *selectedBus = (BME688Bus *)intf_ptr;

    if((selectedBus == NULL) || (selectedBus->i2cHandle == NULL) || (registerData == NULL) || (dataLength == 0U) || (dataLength > UINT16_MAX))
	{
	   return (BME68X_INTF_RET_TYPE)-1;
	}
    //HAL_StatusTypeDef HAL_I2C_Mem_Write(I2C_HandleTypeDef *hi2c, uint16_t DevAddress, uint16_t MemAddress, uint16_t MemAddSize, uint8_t *pData, uint16_t Size, uint32_t Timeout)
    HAL_StatusTypeDef halStatus = HAL_I2C_Mem_Write(selectedBus->i2cHandle,(uint16_t)(selectedBus->address7Bit << 1U), reg_addr, I2C_MEMADD_SIZE_8BIT, (uint8_t *)registerData, (uint16_t)dataLength, BME688_I2C_TIMEOUT_MS);


	if(halStatus == HAL_OK){
	  return BME68X_INTF_RET_SUCCESS;
	}

    return (BME68X_INTF_RET_TYPE)-1;
}

static void BME688_DelayMicroseconds(uint32_t periodMicroseconds, void *intf_ptr)
{
	(void)intf_ptr; //ovo je tu samo zato sto prema senzoru moramo dati ovaj parametar, ali on nam za cekanje ne treba, na ovaj nacin nece bit upozorenja za unused param


	//ovih +999 je zaokruzivanje prema gore jer se kod djeljenja uzima samo cijeli broj, bez toga - zaokruzilo bi se prema dolje
	uint32_t periodMilliseconds = (periodMicroseconds + 999U) / 1000U;

	HAL_Delay(periodMilliseconds);
}




HAL_StatusTypeDef BME688Sensor_Init(I2C_HandleTypeDef *i2cHandle)
{
	if (i2cHandle == NULL)
	{
	     return HAL_ERROR;
	}

	bus.i2cHandle = i2cHandle;
	isInitialized = 0U;

	lastDriverResult = tryAddress(BME68X_I2C_ADDR_LOW);
	if(lastDriverResult != BME68X_OK)
	{
		lastDriverResult = tryAddress(BME68X_I2C_ADDR_HIGH);
	}

	if(lastDriverResult != BME68X_OK)
	{
		 return HAL_ERROR;
	}


   memset(&sensorConfiguration, 0, sizeof(sensorConfiguration));
   sensorConfiguration.filter = BME68X_FILTER_OFF;
   sensorConfiguration.odr = BME68X_ODR_NONE;
   sensorConfiguration.os_hum = BME68X_OS_16X;
   sensorConfiguration.os_pres = BME68X_OS_1X;
   sensorConfiguration.os_temp = BME68X_OS_2X;

   lastDriverResult = bme68x_set_conf(&sensorConfiguration, &device);
   if(lastDriverResult != BME68X_OK)
   {
       return HAL_ERROR;
   }

   memset(&heaterConfiguration, 0, sizeof(heaterConfiguration));
   heaterConfiguration.enable = BME68X_ENABLE;
   heaterConfiguration.heatr_temp = BME688_HEATER_TEMPERATURE_C;
   heaterConfiguration.heatr_dur = BME688_HEATER_DURATION_MS;


   lastDriverResult = bme68x_set_heatr_conf(BME68X_FORCED_MODE, &heaterConfiguration, &device);
   if(lastDriverResult != BME68X_OK)
   {
      return HAL_ERROR;
   }

   isInitialized = 1U;
   return HAL_OK;

}


HAL_StatusTypeDef BME688Sensor_Read(BME688Reading *reading)
{
	if((isInitialized == 0U) || (reading == NULL))
	{
	    return HAL_ERROR;
	}

	lastDriverResult = bme68x_set_op_mode(BME68X_FORCED_MODE, &device);
	if (lastDriverResult != BME68X_OK)
	{
	    return HAL_ERROR;
	}


	uint32_t measurementDurationMicrosecond = bme68x_get_meas_dur(BME68X_FORCED_MODE, &sensorConfiguration, &device);
	measurementDurationMicrosecond +=((uint32_t)heaterConfiguration.heatr_dur * 1000U);

	device.delay_us(measurementDurationMicrosecond, device.intf_ptr);

	struct bme68x_data sensorData;
	uint8_t numberOfNewMeasurements = 0U; // force mode - 1
	memset(&sensorData, 0, sizeof(sensorData));

	lastDriverResult = bme68x_get_data(BME68X_FORCED_MODE, &sensorData, &numberOfNewMeasurements, &device);
	if((lastDriverResult != BME68X_OK) || (numberOfNewMeasurements == 0U))
	{
		  return HAL_ERROR;
	}

	reading->temperatureC = sensorData.temperature;
	reading->humidityPercent = sensorData.humidity;
	reading->pressureHpa = sensorData.pressure / 100.0f;
	reading->gasResistanceOhm = sensorData.gas_resistance;
	reading->gasValid = ((sensorData.status & BME68X_GASM_VALID_MSK) != 0U) ? 1U : 0U;
	reading ->heaterStable = ((sensorData.status & BME68X_HEAT_STAB_MSK) != 0U) ? 1U : 0U;

	return HAL_OK;

}
