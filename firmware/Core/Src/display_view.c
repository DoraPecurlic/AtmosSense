/*
 * display_view.c
 *
 *  Created on: Aug 6, 2026
 *      Author: Dora_
 */
#include "display_view.h"
#include "ssd1306_fonts.h"
#include "ssd1306.h"

#include <stdio.h>

#define DISPLAY_TEXT_BUFFER_SIZE 32U


void DisplayView_Init(void)
{
	ssd1306_Init();
	ssd1306_Fill(White);
	ssd1306_UpdateScreen();

	  HAL_Delay(5000U);
}

void DisplayView_ShowStartup(void)
{
	ssd1306_Fill(Black);

	 ssd1306_SetCursor(29U, 0U);
	 ssd1306_WriteString("ATMOSSENSE", Font_7x10, White);

	 ssd1306_SetCursor(50U, 12U);
	 ssd1306_WriteString("EDGE", Font_7x10, White);

	 ssd1306_Line(15U, 25U, 112U, 25U, White);

	 ssd1306_SetCursor(1U, 31U);
	 ssd1306_WriteString("Environmental Monitor",Font_6x8,White);

	 ssd1306_SetCursor(31U, 48U);
	 ssd1306_WriteString("Starting...", Font_6x8, White);

	 ssd1306_UpdateScreen();
}



void DisplayView_ShowEnvironment(const SerialTelemetryReading *reading)
{
	 char textBuffer[DISPLAY_TEXT_BUFFER_SIZE];

	 float gasResistanceKOhm ;


	 if (reading == NULL){return;}

	 gasResistanceKOhm= (float)reading->gasResistanceOhm / 1000.0f;

	 ssd1306_Fill(Black);
	 ssd1306_SetCursor(0U, 0U);
	 ssd1306_WriteString("ENVIRONMENT", Font_6x8, White);

	 ssd1306_SetCursor(110U, 0U);
	 ssd1306_WriteString("1/2", Font_6x8, White);

	 ssd1306_Line(0U, 10U, 127U, 10U, White);



	 snprintf(textBuffer, sizeof(textBuffer), "Temperature: %.1fC", reading ->temperatureC);

	 ssd1306_SetCursor(0U, 25U);
	 ssd1306_WriteString(textBuffer, Font_6x8, White);


	 snprintf(textBuffer, sizeof(textBuffer), "Humidity: %.1f %%", reading ->humidityPercent);

	 ssd1306_SetCursor(0U, 35U);
	 ssd1306_WriteString(textBuffer, Font_6x8, White);

	 snprintf(textBuffer, sizeof(textBuffer),"Pressure:%.1f hPa", reading->pressureHpa);
	 ssd1306_SetCursor(0U, 45U);
	 ssd1306_WriteString(textBuffer, Font_6x8, White);


	 snprintf(textBuffer, sizeof(textBuffer),"Gas:%.1f kOhm",   gasResistanceKOhm);
	 ssd1306_SetCursor(0U, 56U);
	 ssd1306_WriteString(textBuffer, Font_6x8, White);



	 ssd1306_UpdateScreen();

}

void DisplayView_ShowLight(const SerialTelemetryReading *reading)
{

    if (reading == NULL)
    {
        return;
    }

    char textBuffer[DISPLAY_TEXT_BUFFER_SIZE];
    ssd1306_Fill(Black);


    ssd1306_SetCursor(0U, 0U);
    ssd1306_WriteString("LIGHT", Font_6x8, White);

    ssd1306_SetCursor(110U, 0U);
    ssd1306_WriteString("2/2", Font_6x8, White);

    ssd1306_Line(0U, 10U, 127U, 10U, White);



    snprintf(textBuffer,sizeof(textBuffer),"Clear: %u",(unsigned int)reading->clearRaw);
    ssd1306_SetCursor(0U, 17U);
    ssd1306_WriteString(textBuffer, Font_6x8, White);

    snprintf(textBuffer,sizeof(textBuffer),"Red: %u",(unsigned int)reading->redRaw);
    ssd1306_SetCursor(0U, 25U);
    ssd1306_WriteString(textBuffer, Font_6x8, White);

    snprintf(textBuffer,sizeof(textBuffer),"Green: %u",(unsigned int)reading->greenRaw);
    ssd1306_SetCursor(0U, 35U);
    ssd1306_WriteString(textBuffer, Font_6x8, White);

    snprintf(textBuffer,sizeof(textBuffer),"Blue: %u",(unsigned int)reading->blueRaw);
    ssd1306_SetCursor(0U, 45U);
    ssd1306_WriteString(textBuffer, Font_6x8, White);


    snprintf(textBuffer,sizeof(textBuffer),"Proximity: %u",(unsigned int)reading->proximityRaw);
    ssd1306_SetCursor(0U, 56U);
    ssd1306_WriteString(textBuffer, Font_6x8, White);

    ssd1306_UpdateScreen();

}











