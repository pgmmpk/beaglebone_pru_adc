## Driver memory map

This is the structure of local PRU0 memory. There are 512 bytes available (128 fullwords)

```
Offset       Length  Value         Name       Description
------       ------  -----         ----       -----------
0x0000            4  0xbeef1965    EYE        Eyecatcher constant 0xbeef1965
0x0004            4  0x00000000    TICKS      Number of capture ticks. Incremented each time ADC capture runs (200K times per sec, approx)
0x0008            4  0x00000000    FLAGS      Execution flags (bit mapped)
0x000c            4  0x00000000    SCOPE_OUT  Address of the DDR memory buffer where to store OSCILLOSCOPE captured values
0x0010            4  0x00000000    SCHOPE_OFF Offset to use for OSCILLOSCOPE capture
0x0014            4  0x00000000    SCOPE_LEN  How many values to capture in OSCILLOSCOPE mode
0x0018            4  0x00000000    DEBUG_VAL  Value to be stored for debugging purpose
0x001c            4  0x00000000    EMA_POW    Exponent to use for 	EMA-averaging: ema_value += (value - ema_value / 2^EMA_POW)
0x0020            4  0x00000000    AIN0_EMA   Value (optionally smoothened via EMA) of the channel AIN0
0x0024            4  0x00000000    AIN1_EMA   Value (optionally smoothened via EMA) of the channel AIN1
0x0028            4  0x00000000    AIN2_EMA   Value (optionally smoothened via EMA) of the channel AIN2
0x002c            4  0x00000000    AIN3_EMA   Value (optionally smoothened via EMA) of the channel AIN3
0x0030            4  0x00000000    AIN4_EMA   Value (optionally smoothened via EMA) of the channel AIN4
0x0034            4  0x00000000    AIN5_EMA   Value (optionally smoothened via EMA) of the channel AIN5
0x0038            4  0x00000000    AIN6_EMA   Value (optionally smoothened via EMA) of the channel AIN6
0x003c            4  0x00000000    AIN7_EMA   Value (optionally smoothened via EMA) of the channel AIN7
0x0040            4  0x00000000    ENC_CHNLS  Encoder channels
0x0044            4  0x00000800    ENC_THRSH  Schmitt trigger threshold for encoder values
0x0048            4  0x00000000    ENC0_RAW   Raw value last captured for ENC0
0x004c            4  0x00000000    ENC0_MIN   Running min (see Scmitt trigger filtering algo)
0x0050            4  0x00000000    ENC0_MAX   Running max (see Scmitt trigger filtering algo)
0x0054            4  0x00000000    ENC0_TICK  Number of ticks for encoder 0
0x0058            4  0x00000000    ENC0_SPD   Speed for the encoder 0
0x005c            4  0x00000000    ENC0_ACC   Accumulator for computing encoder speed
0x0060            4  0x00000000    ENC0_DELAY Signal must exceed threshold for at least this value to be registered
0x0064            4  0x00000000    ENC0_UP    Counts how many timer units signal is over the threshold
0x0068            4  0x00000000    ENC0_DOWN  Counts how many timer units signal is below the threshold
0x006c            4                           Reserved
0x0070            4                           Reserved
0x0074            4                           Reserved
0x0078            4                           Reserved
0x007c            4                           Reserved
0x0080            4                           Reserved
0x0084            4  0x00000800    ENC_THRSH  Schmitt trigger threshold for encoder values
0x0088            4  0x00000000    ENC1_RAW   Raw value last captured for ENC1
0x008c            4  0x00000000    ENC1_MIN   Running min (see Scmitt trigger filtering algo)
0x0090            4  0x00000000    ENC1_MAX   Running max (see Scmitt trigger filtering algo)
0x0094            4  0x00000000    ENC1_TICK  Number of ticks for encoder 1
0x0098            4  0x00000000    ENC1_SPD   Speed for the encoder 1
0x009c            4  0x00000000    ENC1_ACC   Accumulator for computing encoder speed
0x00a0            4  0x00000000    ENC1_DELAY Signal must exceed threshold for at least this value to be registered
0x00a4            4  0x00000000    ENC1_UP    Counts how many timer units signal is over the threshold
0x00a8            4  0x00000000    ENC1_DOWN  Counts how many timer units signal is below the threshold
0x00ac            4                           Reserved
0x00b0            4                           Reserved
0x00b4            4                           Reserved
0x00b8            4                           Reserved
0x00bc            4                           Reserved
0x00c0            4                           Reserved
0x00c4            4  0x00000000    CAP_DELAY  Extra delay to control capture frequency
```
