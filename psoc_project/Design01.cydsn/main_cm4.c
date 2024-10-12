#include "project.h"

#include "game.h"


int main(void)
{
    __enable_irq();
    
    game_start();
    game_run();

    for(;;) {}
}
