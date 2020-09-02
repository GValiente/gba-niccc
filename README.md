# GBA-NICCC

Game Boy Advance port of the Atari ST demo STNICCC 2000 by Oxygene.

Scene data provided by [st-niccc-2000-html5 port](https://github.com/dabadab/st-niccc-2000-html5).

## Features

* 60FPS :)

* It plays the original music thanks to [maxmod](https://maxmod.devkitpro.org/).

* Huge ROM size :(

* An antialiased BW mode can be enabled by pressing A.
  
* The CPU is at 60% at most.

* The renderer could handle more complex scenes easily.

* I could have added some compression too.

* It shouldn't work on shitty flash cards.

## How to build

[butano](https://github.com/GValiente/butano) is required to build this port.

By default it should be placed in `/path/to/gba-niccc/../butano`, but if you have it in another path you can modify the Makefile of this project.

Type `make -j<number_of_cpu_cores>` and wait a bit.

## How to regenerate the input data

Input data needed by this project is already generated in the `data` folder.

However, if you want to regenerate it execute the `main.py` script located in the `data_generator` folder.
