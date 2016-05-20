#Makefile for STM32CubeMX

This program generates a Makefile from STM32CubeMX (http://www.st.com/stm32cube) created project. 

author: Juraj Dudak


Date: 16/03/2016

Version: 1.3.0

 - New
 	- add Debug support for st-util app (github texane/stlink)
 	- Automatic debug build
 - How to use Debug mode:
 	- in terminal run: st-util
 	- in C::B, choose "Debug" build target
 	- rebuild project
 	- run Debug (F8)
 - Remove
 	- remove build option from command line. The buld option is dona automaticaly by Makefile (make Debug or make Release).

----------------------------

Date: 13/02/2016

Version: 1.2.0

 - Fix
 	- correct mcpu flag with STM32L0 MCU
 	- add correct settings flag __weak and __packed from SW4STM32 project file
 - Add size reducing flags in makefile: nano.specs, nosys.specs
 - add code generation for debugging in Code::Blocks IDE project

----------------------------

Date: 07/02/2016

Version: 1.1.0

 - add commandline switches:
 	- build=Debug/Release : For debugging purpose
 	- opt=0/1/2/s : for code optimalization
 - support code generation from Middleware folder (from ST examples), 
 - add code generation for debugging in Code::Blocks IDE project

----------------------------

Date: 01/11/2015

Version: 1.0.0

original work: https://github.com/baoshi/CubeMX2Makefile

-----------------------------

Changes and Improvements:

 - support only SW4STM32 projects, because there is bug in generation code for TrueStudio in Linux
 - add all .c files in Src directory into project and Makefile
 - makefile is prepared for Code::Blocks IDE (flashing bin program after compile)
 - create project file for Code::Blocks

## Instalation
	sudo ln -s "$PWD"/CubeMX2Makefile.py /usr/bin/CubeMX2Makefile.py

## Dependencies
 - flashing tool "st-flash" - https://github.com/texane/stlink
 - gcc-arm-none-eabi
 - libnewlib-arm-none-eabi

## Usage
	CubeMX2Makefile.py <path_to_cube_project> -opt={0|1|2|s}

### Usage of generated Makefile
- "make" : compile, build and flash program to MCU
- "make Release" : the same as "make". It is for Code::Blocks environment
- "make Debug" : compile and build only (there is no real debug)
- "make clean" : clean builded files
- "make flash" : flash code to MCU

##Output
 - Makefile with prepared rules for Code::Block IDE
 - Code::Block project file

## Disclaimer
Copyright 2015 Juraj Dudak

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.