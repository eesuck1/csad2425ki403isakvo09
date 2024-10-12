#ifndef GAME_H
#define GAME_H
    
#include <stdio.h>
#include <stdlib.h>
    
#include "project.h"    

#include "types.h"
#include "constants.h"
#include "communication.h"

static u8 game_running = 1u;
static u8 man_turn = 1u;
    
static u8 figures[CELLS_NUMBER * CELLS_NUMBER];
static game_type type = UNKNOWN;

static u8 game_packet[GAME_TYPE_PACKET_LENGTH];
static u8 man_vs_man_packet[GAME_TYPE_PACKET_LENGTH];
static u8 man_vs_ai_packet[GAME_TYPE_PACKET_LENGTH];
static u8 ai_vs_ai_packet[GAME_TYPE_PACKET_LENGTH];
static u8 reset_packet[GAME_TYPE_PACKET_LENGTH];

static u8 win_packet[CELLS_NUMBER * CELLS_NUMBER];
static u8 ack_packet[CELLS_NUMBER * CELLS_NUMBER];


static inline void clear_board(void)
{
    for (u8 i = 0u; i < CELLS_NUMBER; i++)
        for (u8 j = 0u; j < CELLS_NUMBER; j++)
        {
            figures[i * CELLS_NUMBER + j] = EMPTY;
        }
}

static inline void set_figure(u8 x, u8 y)
{
    static u8 figure_index = 0u;
    
    if (figures[x * CELLS_NUMBER + y] == EMPTY)
    {
        figures[x * CELLS_NUMBER + y] = figure_index;
        figure_index = !figure_index;
    }
}

static inline void init_packets(void)
{
    for (u8 index = 0u; index < CELLS_NUMBER * CELLS_NUMBER; index++)
    {
        ack_packet[index] = ACK_PACKET_VALUE;
        win_packet[index] = NO_WINNER_PACKET_VALUE;
    }
    
    for (u8 index = 0u; index < GAME_TYPE_PACKET_LENGTH; index++)
    {
        game_packet[index] = UNKNOWN_PACKET_VALUE;
        man_vs_man_packet[index] = MAN_VS_MAN_PACKET_VALUE;
        man_vs_ai_packet[index] = MAN_VS_AI_PACKET_VALUE;
        ai_vs_ai_packet[index] = AI_VS_AI_PACKET_VALUE;
        reset_packet[index] = RESET_PACKET_VALUE;
    }
}

static inline void send_ack(u8 *packet)
{   
    return;
    
    send_message(ack_packet, CELLS_NUMBER * CELLS_NUMBER);
    receive_message(game_packet, GAME_TYPE_PACKET_LENGTH);
    
    while (memcmp(game_packet, packet, GAME_TYPE_PACKET_LENGTH) == 0)
    {
        send_message(ack_packet, CELLS_NUMBER * CELLS_NUMBER);
        receive_message(game_packet, GAME_TYPE_PACKET_LENGTH);
    }
}

static inline void recieve_game_type(void)
{
    u8 recieved = FALSE;
    
    while (!recieved)
    {
        receive_message(game_packet, GAME_TYPE_PACKET_LENGTH);
        
        if (memcmp(game_packet, man_vs_man_packet, GAME_TYPE_PACKET_LENGTH) == 0)
        {
            type = MAN_VS_MAN;
            
            send_ack(man_vs_man_packet);
        }
        else if (memcmp(game_packet, man_vs_ai_packet, GAME_TYPE_PACKET_LENGTH) == 0)
        {
            type = MAN_VS_AI;
            
            send_ack(man_vs_ai_packet);
        }
        else if (memcmp(game_packet, ai_vs_ai_packet, GAME_TYPE_PACKET_LENGTH) == 0)
        {
            type = AI_VS_AI;
            
            send_ack(ai_vs_ai_packet);
        }
        else
            continue;
        
        recieved = TRUE;
    }
}

static inline void game_reset(void)
{
    type = UNKNOWN;
    game_running = 1u;
    
    clear_board();
    init_packets();
    recieve_game_type();
}
    
static inline void game_start(void)
{
    communication_start();
    clear_board();
    init_packets();
    recieve_game_type();
}

static inline void check_events(void)
{
    receive_message(game_packet, GAME_TYPE_PACKET_LENGTH);
    
    if (memcmp(game_packet, reset_packet, GAME_TYPE_PACKET_LENGTH) == 0)
    {
        send_ack(game_packet);
        game_reset();
        
        return;
    }
    if (!game_running)
    {       
        send_message(win_packet, CELLS_NUMBER * CELLS_NUMBER);
        
        CyDelay(50u);
        
        return;
    }
    
    switch (type)
    {
        case MAN_VS_MAN:
        {
            if ((game_packet[0u] - 1u < CELLS_NUMBER) && (game_packet[1u] - 1u < CELLS_NUMBER))
            {
                send_ack(game_packet);
                set_figure(game_packet[0u] - 1u, game_packet[1u] - 1u);
                send_message(figures, 9u);
            }
            
            break;
        }
        case MAN_VS_AI:
        {
            if ((game_packet[0u] - 1u < CELLS_NUMBER) && (game_packet[1u] - 1u < CELLS_NUMBER) && man_turn)
            {
                send_ack(game_packet);
                set_figure(game_packet[0u] - 1u, game_packet[1u] - 1u);
                
                man_turn = !man_turn;
            }
            else if (!man_turn)
            {
                send_ack(game_packet);
                
                u8 x = rand() % 3;
                u8 y = rand() % 3;
                
                while (figures[x * CELLS_NUMBER + y] != EMPTY)
                {
                    x = rand() % 3;
                    y = rand() % 3;
                }
                
                set_figure(x, y);
                man_turn = !man_turn;
                
                CyDelay(50u);
            }
            
            send_message(figures, 9u);
            
            break;
        }
        case AI_VS_AI:
        {
            send_ack(game_packet);
            set_figure(rand() % 3, rand() % 3);
            send_message(figures, 9u);

            CyDelay(50u);
            
        }
        case UNKNOWN:
        default:
        {
            send_ack(game_packet);
            break;
        }
    }
}

static inline void check_win(void)
{
    for (u8 index = 0u; index < CELLS_NUMBER * CELLS_NUMBER; index++)
    {
        if (figures[index] == EMPTY)
        {
            game_running = 1u;
            
            break;
        }
        else
        {
            game_running = 0u;
        }
    }
    
    for (u8 i = 0u; i < 8u; i++)
    {
        u32 accumulator = 0u;
        
        for (u8 j = 0u; j < CELLS_NUMBER * CELLS_NUMBER; j++)
            accumulator += figures[j] & win_masks[i][j];
            
        if (accumulator == 0u)
        {
            game_running = 0u;
            
            for (u8 index = 0u; index < CELLS_NUMBER * CELLS_NUMBER; index++)
                win_packet[index] = WIN_CROSS_PACKET_VALUE;
        }
        else if (accumulator == 3u)
        {
            game_running = 0u;
            
            for (u8 index = 0u; index < CELLS_NUMBER * CELLS_NUMBER; index++)
                win_packet[index] = WIN_NOD_PACKET_VALUE;
        }
    }
}

static inline void game_run(void)
{
    for (;;)
    {
        check_events();
        check_win();
    }
}
    
#endif
    