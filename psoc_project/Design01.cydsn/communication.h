#ifndef COMMUNICATION_H
#define COMMUNICATION_H
    
#include <stdio.h>
#include <string.h>
    
#include "project.h"
#include "types.h"
#include "constants.h"
    
static u8 communication_receive_buffer[RECEIVE_BUFFER_LENGTH];
static u8 communication_send_buffer[SEND_BUFFER_LENGTH];

static inline void communication_start(void)
{
    UART_Start();
    setvbuf(stdin, NULL, _IONBF, 0);
}
 
static inline void receive_message(u8 *buffer, u8 length)
{
    if ((length + 2u > RECEIVE_BUFFER_LENGTH) || buffer == NULL) return;
    
    UART_GetArrayBlocking(communication_receive_buffer, length + 2u);
    
    if ((communication_receive_buffer[0] == PACKET_START_VALUE) 
        && (communication_receive_buffer[length + 1u] == PACKET_END_VALUE))
    {
        for (u8 index = 0u; index < length; index++)
            buffer[index] = communication_receive_buffer[index + 1u];
            
        memset(communication_receive_buffer, 0u, RECEIVE_BUFFER_LENGTH);
    }
}

static inline void send_message(u8 *buffer, u8 length)
{
    if ((length + 2u > SEND_BUFFER_LENGTH) || buffer == NULL) return;

    communication_send_buffer[0] = PACKET_START_VALUE;
    communication_send_buffer[length + 1u] = PACKET_END_VALUE;
    
    for (u8 index = 1u; index < length + 1u; index++)
        communication_send_buffer[index] = buffer[index - 1u];
        
    UART_PutArrayBlocking(communication_send_buffer, SEND_BUFFER_LENGTH);
    
    memset(communication_send_buffer, 0u, SEND_BUFFER_LENGTH);
}

#endif // COMMUNICATION_H