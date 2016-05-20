########################################################
# Makefile by CubeMX2Makefile.py
########################################################
# Path to gcc
GCC_PATH = /usr/bin/
#GCC_PATH = /home/juraj/Programy/arm_compiler5/bin/
# Path to st-flash tool
FLASH_PATH = /usr/local/bin/st-flash

########################################################
# target
########################################################
TARGET = $TARGET

########################################################
# building variables
########################################################
# optimization
OPT = $CODE_OPTIMALIZATION

#########################################################
# pathes
#########################################################
# source path
# Build path
BUILD_DIR = build

########################################################
# source
########################################################
$C_SOURCES  
$ASM_SOURCES

#######################################
# binaries
#######################################
PREFIX  = $$(GCC_PATH)arm-none-eabi-
CC = $$(PREFIX)gcc
AS = $$(PREFIX)gcc -x assembler-with-cpp
CP = $$(PREFIX)objcopy
AR = $$(PREFIX)ar
SZ = $$(PREFIX)size
HEX = $$(CP) -O ihex
BIN = $$(CP) -O binary -S
 
#########################################################
# CFLAGS
#########################################################
# macros for gcc
$AS_DEFS
$C_DEFS
# includes for gcc
$AS_INCLUDES
$C_INCLUDES
# compile gcc flags
WFLAGS = -Wall -fdata-sections -ffunction-sections -fmessage-length=0 -c
ASFLAGS = $MCU $$(AS_DEFS) $$(AS_INCLUDES) $$(OPT) $$(WFLAGS)
CFLAGS = $MCU -fno-aggressive-loop-optimizations $$(C_DEFS) $$(C_INCLUDES) $$(OPT) $$(WFLAGS)
# Generate dependency information
CFLAGS += -MD -MP -MF .dep/$$(@F).d

#########################################################
# LDFLAGS
#########################################################
# link script
LDSCRIPT = $LD_SCRIPT
# libraries
LIBS = -lc -lm -lnosys
LIBDIR =
CC_VER := $$(shell $$(CC) -dumpversion)
ifeq "$$(CC_VER)" "4.8.2"
	LDSPECS = -specs=nosys.specs 
else
	LDSPECS = -specs=nano.specs -specs=nosys.specs 
endif
LDFLAGS = $MCU $$(LDSPECS) -T$$(LDSCRIPT) $$(LIBDIR) $$(LIBS) -Wl,-Map=$$(BUILD_DIR)/$$(TARGET).map,--cref -Wl,--gc-sections

# default action: build all
all: $$(BUILD_DIR)/$$(TARGET).elf $$(BUILD_DIR)/$$(TARGET).hex $$(BUILD_DIR)/$$(TARGET).bin

#########################################################
# build the application
#########################################################
# list of objects
OBJECTS = $$(addprefix $$(BUILD_DIR)/,$$(notdir $$(C_SOURCES:.c=.o)))
vpath %.c $$(sort $$(dir $$(C_SOURCES)))
# list of ASM program objects
OBJECTS += $$(addprefix $$(BUILD_DIR)/,$$(notdir $$(ASM_SOURCES:.s=.o)))
vpath %.s $$(sort $$(dir $$(ASM_SOURCES)))

$$(BUILD_DIR)/%.o: %.c Makefile | $$(BUILD_DIR) 
	@echo "C. Compiling $$@..."
	@$$(CC) -c $$(CFLAGS) -Wa,-a,-ad,-alms=$$(BUILD_DIR)/$$(notdir $$(<:.c=.lst)) $$< -o $$@

$$(BUILD_DIR)/%.o: %.s Makefile | $$(BUILD_DIR)
	@echo "S. Compiling $$@..."
	@$$(AS) -c $$(CFLAGS) $$< -o $$@

$$(BUILD_DIR)/$$(TARGET).elf: $$(OBJECTS) Makefile
	@echo "C. Linking $$@..."
	@$$(CC) $$(OBJECTS) $$(LDFLAGS) -o $$@
	$$(SZ) $$@

$$(BUILD_DIR)/%.hex: $$(BUILD_DIR)/%.elf | $$(BUILD_DIR)
	@echo "H. Linking $$@..."
	@$$(HEX) $$< $$@
	
$$(BUILD_DIR)/%.bin: $$(BUILD_DIR)/%.elf | $$(BUILD_DIR)
	@echo "B. Building $$@..."
	@$$(BIN) $$< $$@	
	@echo "Used gcc: "$$(CC_VER)
	
$$(BUILD_DIR):
	mkdir -p $$@		

#########################################################
# clean up
#########################################################
clean:
	-rm -fR .dep $$(BUILD_DIR)
  
#########################################################
# Code::Blocks commands:
#########################################################
Release: all flash
Debug: CFLAGS += -g -gdwarf-2
Debug: all
cleanDebug: clean
cleanRelease: clean
flash:
	$$(FLASH_PATH) erase
	$$(FLASH_PATH) --reset write $$(BUILD_DIR)/$$(TARGET).bin 0x8000000

#########################################################
# dependencies
#########################################################
-include $$(shell mkdir .dep 2>/dev/null) $$(wildcard .dep/*)

# *** EOF ***
