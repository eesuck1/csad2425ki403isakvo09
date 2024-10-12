#ifndef CONSTANTS_H
#define CONSTANTS_H
    
#include "types.h"
    
#define TRUE                     1u
#define FALSE                    0u
    
#define RECEIVE_BUFFER_LENGTH    4u
#define SEND_BUFFER_LENGTH       11u

#define GAME_TYPE_PACKET_LENGTH  2u
    
#define CELLS_NUMBER             3u
    
#define UNKNOWN_PACKET_VALUE     0xAA
#define MAN_VS_MAN_PACKET_VALUE  0xBB
#define MAN_VS_AI_PACKET_VALUE   0xCC
#define AI_VS_AI_PACKET_VALUE    0xDD
#define ACK_PACKET_VALUE         0xEE
#define RESET_PACKET_VALUE       0x99
#define WIN_CROSS_PACKET_VALUE   0x88
#define WIN_NOD_PACKET_VALUE     0x77
#define NO_WINNER_PACKET_VALUE   0x22
    
#define PACKET_START_VALUE       '<'
#define PACKET_END_VALUE         '>'
    
    
const u8 win_masks[8u][CELLS_NUMBER * CELLS_NUMBER] = {
    {0xFF, 0xFF, 0xFF, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 0xFF, 0xFF, 0xFF, 0, 0, 0},
    {0, 0, 0, 0, 0, 0, 0xFF, 0xFF, 0xFF},
    {0xFF, 0, 0, 0xFF, 0, 0, 0xFF, 0, 0},
    {0, 0xFF, 0, 0, 0xFF, 0, 0, 0xFF, 0},
    {0, 0, 0xFF, 0, 0, 0xFF, 0, 0, 0xFF},
    {0xFF, 0, 0, 0, 0xFF, 0, 0, 0, 0xFF},
    {0, 0, 0xFF, 0, 0xFF, 0, 0xFF, 0, 0},
};
    
#endif // CONSTANTS_H