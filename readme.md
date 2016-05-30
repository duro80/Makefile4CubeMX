#Makefile for STM32CubeMX

This program generates a Makefile from STM32CubeMX (http://www.st.com/stm32cube) created project. 

author: Juraj Dudak

Date: 16/03/2016

-----------------------------

Changes and Improvements:

 - support only SW4STM32 projects, because there is (was) bug in generation code for TrueStudio in Linux
 - add all .c files in Src directory into project and Makefile
 - makefile is prepared for Code::Blocks IDE (flashing bin program after compile)
 - create project file for Code::Blocks

## Instalation
	sudo ./install

## Dependencies
 - flashing tool "st-flash" - https://github.com/texane/stlink
 - gcc-arm-none-eabi
 - libnewlib-arm-none-eabi

## Usage
	CubeMX2Makefile.py <path_to_cube_project> [-opt={0|1|2|s}]

Example of use: open terminal in directory, where CubeMX generated the SW4STM32 project:
	CubeMX2Makefile.py .	

You can overwrtie default setting by editing local.settings file. See the local.setting file for details.

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