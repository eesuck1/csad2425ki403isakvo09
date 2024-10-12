#ifndef TYPES_H
#define TYPES_H

#include <stdint.h>

typedef int64_t s64;
typedef int32_t s32;
typedef int16_t s16;
typedef int8_t s8;

typedef uint64_t u64;
typedef uint32_t u32;
typedef uint16_t u16;
typedef uint8_t u8;

typedef long double f80;
typedef double f64;
typedef float f32;
    
typedef enum __figure_type
{
    CROSS = 0u,
    NOD   = 1u,
    EMPTY = 0xFF
} figure_type;

typedef enum __game_type
{
    UNKNOWN = 0u,
    MAN_VS_MAN,
    MAN_VS_AI,
    AI_VS_AI,
} game_type;

#endif // TYPES_H
