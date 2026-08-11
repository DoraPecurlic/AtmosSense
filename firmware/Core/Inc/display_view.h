/*
 * display_view.h
 *
 *  Created on: Aug 6, 2026
 *      Author: Dora_
 */

#ifndef INC_DISPLAY_VIEW_H_
#define INC_DISPLAY_VIEW_H_

#include "serial_telemetry.h"

void DisplayView_Init(void);

void DisplayView_ShowStartup(void);
void DisplayView_ShowEnvironment(const SerialTelemetryReading *reading);
void DisplayView_ShowLight(const SerialTelemetryReading *reading);

#endif /* INC_DISPLAY_VIEW_H_ */
