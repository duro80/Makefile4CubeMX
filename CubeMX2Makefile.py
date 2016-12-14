#!/usr/bin/env python

import sys
import re
import shutil
import os.path
from string import Template
from xml.etree import ElementTree as ET
import subprocess
import os

C2M_ERR_SUCCESS             =  0
C2M_ERR_INVALID_COMMANDLINE = -1
C2M_ERR_LOAD_TEMPLATE       = -2
C2M_ERR_NO_PROJECT          = -3
C2M_ERR_PROJECT_FILE        = -4
C2M_ERR_IO                  = -5
C2M_ERR_NEED_UPDATE         = -6

# STM32 part to compiler flag mapping
mcu_cflags = {}
mcu_cflags[re.compile('STM32F0')] = '-mthumb -mcpu=cortex-m0'
mcu_cflags[re.compile('STM32L0')] = '-mthumb -mcpu=cortex-m0plus'
mcu_cflags[re.compile('STM32(F|L)1')] = '-mthumb -mcpu=cortex-m3'
mcu_cflags[re.compile('STM32(F|L)2')] = '-mthumb -mcpu=cortex-m3'
mcu_cflags[re.compile('STM32(F|L)3')] = '-mthumb -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 -mfloat-abi=softfp'
mcu_cflags[re.compile('STM32(F|L)4')] = '-mthumb -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 -mfloat-abi=softfp'
mcu_cflags[re.compile('STM32(F|L)7')] = '-mthumb -mcpu=cortex-m7 -mfpu=fpv5-sp-d16 -mfloat-abi=softfp'

workdir =  os.path.dirname(os.path.realpath(__file__))
file_local_settings =workdir+"/local.settings"
localSetting={}
localSetting["GCC_PATH"]="/usr/bin/"
localSetting["FLASH_PATH"]="/usr/local/bin/st-flash"
localSetting["GDB_IP_PORT"]="4242"
localSetting["GDP_IP_ADDRESS"]="localhost"

try:
    hfile = open(file_local_settings,"r")
    lines = hfile.readlines()
    for line in lines:
        line = line.strip()
        if len(line)>0:
            if line[0]=='#':
                continue
            v1,v2 = line.split("=")
            v1 = v1.strip()
            v2 = v2.strip()
            localSetting[v1]=v2
    hfile.close()
except:
    sys.stderr.write("No or damaged config file. Default settings will be used\r\n")
    sys.stderr.write("---------------------------------------------\r\n")
    try:
        hfile = open(file_local_settings,"w")
        hfile.write("# local configuration for CubeMX2Makefile.py script\r\n")
        hfile.write("#\r\n")
        hfile.write("#------------------------------------------------------------------------------------\r\n")
        hfile.write("# uncomments the required local settings\r\n")
        hfile.write("# supported config are:\r\n")
        hfile.write("#	- GCC_PATH		: specifies the path to gcc toolchain\r\n")
        hfile.write("#	- FLASH_PATH	: specifies the path to stlink utility\r\n")
        hfile.write("#	- GDB_IP_PORT	: specifies the port to GDB server. Default is 4242\r\n")
        hfile.write("#	- GDP_IP_ADDRESS: specifies the address to GDB server. Default is localhost\r\n")
        hfile.write("#------------------------------------------------------------------------------------\r\n")
        hfile.write("\r\n")
        hfile.write("# Part 1: MAKEFILE\r\n")
        hfile.write("#GCC_PATH = \r\n")
        hfile.write("#FLASH_PATH =\r\n")
        hfile.write("\r\n")
        hfile.write("#------------------------------------------------------------------------------------\r\n")
        hfile.write("\r\n")
        hfile.write("# Part 2: Code::Blocks IDE\r\n")
        hfile.write("#GDB_IP_PORT = 4242\r\n")
        hfile.write("#GDP_IP_ADDRESS = localhost\r\n")
    except Exception, e:
        sys.stderr.write(e)
        sys.stderr.write("Error create local.settings file")


if len(sys.argv) < 2:
    sys.stderr.write("\r\nSTM32CubeMX project to Makefile v1.0\r\n")
    sys.stderr.write("-==================================-\r\n")
    sys.stderr.write("Written by Juraj Dudak <juraj\x40dudak.sk> on 2015-06-25\r\n")
    sys.stderr.write("Based on script from Baoshi <mail\x40ba0sh1.com> on 2015-02-22\r\n")
    sys.stderr.write("Apache License 2.0 <http://www.apache.org/licenses/LICENSE-2.0>\r\n")
    sys.stderr.write("For STM32CubeMX Version 4.8.0 http://www.st.com/stm32cube\r\n")
    sys.stderr.write("Usage:\r\n")
    sys.stderr.write("  CubeMX2Makefile.py <STM32CubeMX \"Toolchain Folder Location\">  [-opt={0|1|2|s}\r\n")
    sys.stderr.write("  Default values:\r\n")
    sys.stderr.write("      opt = 2 (-O2 optimalization)\r\n")
    sys.stderr.write("\r\nMakefile usage:\r\n")
    sys.stderr.write("Build project\r\n")
    sys.stderr.write("\tmake\r\n")
    sys.stderr.write("Flash project\r\n")
    sys.stderr.write("\tmake flash\r\n")
    sys.stderr.write("Clean project\r\n")
    sys.stderr.write("\tmake clean\r\n")
    sys.exit(C2M_ERR_INVALID_COMMANDLINE)


# Load template files
app_folder = os.path.dirname(os.path.abspath(sys.argv[0]))

#flag_debug = 0
flag_opt = "-O2"
if len(sys.argv) >= 3:
    n = len(sys.argv) - 2
    for i in range(n):
        value = sys.argv[2+i].split("=")
#        if value[0]=='-build':
#            if value[1][0]=='D':
#                flag_debug = 1
        if value[0]=='-opt':
                flag_opt = "-O" + str(value[1][0])
#print "Build:\t\t\t",
#if flag_debug==1:
#    print "Debug"
#else:
#    print "Release"

print "Code optimalization:\t",flag_opt

if os.path.islink(sys.argv[0]):
    app_folder = os.path.realpath(sys.argv[0])
    app_folder = os.path.dirname(app_folder)

try:
    fd = open(app_folder + os.path.sep + 'CubeMX2Makefile.tpl', 'rb')
    mft = Template(fd.read())
    fd.close()
except Exception, e:
    sys.stderr.write("Unable to load template file CubeMX2Makefile.tpl\r\n")
    sys.stderr.write(e)
    sys.exit(C2M_ERR_LOAD_TEMPLATE)

'''
try:
    fd = open(app_folder + os.path.sep + 'CubeMX2Makefile.tpl', 'rb')
    #check st-flash program exists
    for line in fd.readlines():
        oneLine = line.split("=")
        if len(oneLine)==2:
            if oneLine[0].strip()=="FLASH_PATH":
                flashPath=oneLine[1].strip()
                break
    fd.close()
except:
    sys.stderr.write("Unable to load template file CubeMX2Makefile.tpl\r\n")
    sys.exit(C2M_ERR_LOAD_TEMPLATE)
'''
flash = localSetting["FLASH_PATH"].strip()
#if not os.path.isfile(flashPath):
if not os.path.isfile(flash):
    sys.stderr.write("---------------------WARNING----------------\r\n")
    sys.stderr.write("|- - - - - - - - - - - - - - - - - - - - - -|\r\n")
    sys.stderr.write("|    st-flash utility is not installed.     |\r\n")
    sys.stderr.write("|    Install st-flash from GitHub:          |\r\n")
    sys.stderr.write("|    https://github.com/texane/stlink       |\r\n")
    sys.stderr.write("|- - - - - - - - - - - - - - - - - - - - - -|\r\n")
    sys.stderr.write("--------------------------------------------\r\n")

'''
try:
    fd = open(app_folder + os.path.sep + 'CubeMX2LD.tpl', 'rb')
    ldt = Template(fd.read())
    fd.close()
except:
    sys.stderr.write("Unable to load template file CubeMX2LD.tpl\r\n")
    sys.exit(C2M_ERR_LOAD_TEMPLATE)
'''
proj_folder = os.path.abspath(sys.argv[1])
if not os.path.isdir(proj_folder):
    sys.stderr.write("STM32CubeMX \"Toolchain Folder Location\" %s not found\r\n" % proj_folder)
    sys.exit(C2M_ERR_INVALID_COMMANDLINE)

#detection of multiple project in SW4STM32 folder
n_projects=0
for name in os.listdir(os.path.join(proj_folder,"SW4STM32")):
    n_projects += 1

if n_projects ==1:
    proj_folder_full_path = proj_folder + os.path.sep + 'SW4STM32' + os.path.sep + name
    proj_folder_rel_path = 'SW4STM32' + os.path.sep + name
else:
    print "In project directory are multiple projects."
    n_projects=1
    projects={}
    for name in os.listdir(os.path.join(proj_folder,"SW4STM32")):
        print n_projects,name
        projects[n_projects]=name
        n_projects+=1
    sel_project = input("Select active project: ")
    name = projects[sel_project]
    proj_folder_full_path = proj_folder + os.path.sep + 'SW4STM32' + os.path.sep + name
    proj_folder_rel_path = 'SW4STM32' + os.path.sep + name

ts_project = proj_folder_full_path + os.path.sep + '.project'
ts_cproject = proj_folder_full_path + os.path.sep + '.cproject'
#ts_project = proj_folder + os.path.sep + 'SW4STM32' + os.path.sep + proj_name + ' Configuration' + os.path.sep + '.project'
#ts_cproject = proj_folder + os.path.sep + 'SW4STM32' + os.path.sep + proj_name + ' Configuration' + os.path.sep + '.cproject'

if not (os.path.isfile(ts_project) and os.path.isfile(ts_cproject)):
    sys.stderr.write("SW4STM32 project not found, use STM32CubeMX to generate a SW4STM32 project first\r\n")
    sys.exit(C2M_ERR_NO_PROJECT)
# .project file
try:
    tree = ET.parse(ts_project)
    rootProject = tree.getroot()
except Exception, e:
    sys.stderr.write("Error: cannot parse SW4STM32 .project file: %s\r\n" % ts_project)
    sys.exit(C2M_ERR_PROJECT_FILE)

#name of Makefile project
nodes = rootProject.findall('name')
projectName = nodes[0].text
#proj_name = os.path.splitext(os.path.basename(proj_folder))[0]
proj_name = projectName.split(" ",1)[0]
print "TARGET:\t\t\t", proj_name

nodes = rootProject.findall('linkedResources/link[type=\'1\']/location')
sources = []
sources_set = []
for node in nodes:
    # uprava - syscalls nebude v zdrojakoch
    if node.text.find("syscalls.c")>0:
        continue
    rep = ''
    if node.text.startswith("PARENT-1-PROJECT_LOC"):
        rep = re.sub(r'^PARENT-1-PROJECT_LOC/', '', node.text)
    elif node.text.startswith("PARENT-2-PROJECT_LOC"):
        rep = re.sub(r'^PARENT-2-PROJECT_LOC/', '', node.text)
    elif node.text.startswith("PARENT-7-PROJECT_LOC"):
        rep = re.sub(r'^PARENT-7-PROJECT_LOC/', '', node.text)
    elif node.text.startswith("PARENT-5-PROJECT_LOC"):
        rep = re.sub(r'^PARENT-5-PROJECT_LOC/', '', node.text)
    if rep!='':
        curr_file = rep.split('/')[-1]
        if not curr_file in sources_set:    #eliminate duplicit files in .project
            sources.append(rep)
            sources_set.append(curr_file)
sources = list(set(sources))
sources.sort()
c_sources = 'C_SOURCES ='
asm_sources = 'ASM_SOURCES ='
lib_sources = 'LIB_SOURCES ='
c_sources_list=[]
for source in sources:
    ext = os.path.splitext(source)[1]
    if ext == '.c':
        c_sources += ' \\\n  ' + source
        c_sources_list.append(source)
    elif ext == '.s':
        asm_sources = asm_sources + ' \\\n  ' + source
    else:
        #sys.stderr.write("Unknown source file type: %s\r\n" % source)
        #sys.exit(-5)
        pass
#--------------------------------------------------
# Add files in Src directory to MAKEFILE
#--------------------------------------------------
src_files=[]
for name in os.listdir(os.path.join(proj_folder,"Src")):
    src_files.append(name)
isInList=False
for usr_src in src_files:
    isInList=False
    for csf in c_sources_list:
        if csf.find(usr_src)>=0:
            isInList=True
    if isInList==False:
        c_sources_list.append("Src/"+usr_src)
        c_sources += ' \\\n  ' + "Src/"+usr_src
# .cproject file
try:
    tree = ET.parse(ts_cproject)
    root = tree.getroot()
except Exception, e:
    sys.stderr.write("Error: cannot parse SW4STM32 .cproject file: %s\r\n" % ts_cproject)
    sys.exit(C2M_ERR_PROJECT_FILE)

# Middleware directory
#src_middleware_files=[]
fulldir=os.path.join(proj_folder,"Middlewares")
if os.path.exists(fulldir):
    #print "------MIDDLEWARE------"
    lbf = len(proj_folder)+1
    for koren, subFolders, files in os.walk(fulldir):
        for subor in files:
            if ".c" in subor:
                if subor.find("template",0) >=0:
                    continue
                c_src_file = os.path.join(koren,subor)
                c_src_file = c_src_file[lbf:]
                if c_src_file not in c_sources_list:
					c_sources_list.append(c_src_file)
					c_sources += ' \\\n  ' + c_src_file


fulldir=os.path.join(proj_folder,"Drivers")
fulldir=os.path.join(fulldir,"BSP")
if os.path.exists(fulldir):
    print "------BSP------",
    lbf = len(proj_folder)+1
    for koren, subFolders, files in os.walk(fulldir):
        for subor in files:
            extension = subor.split('.')[1]
            if extension == "c":
                print subor
                c_src_file = os.path.join(koren,subor)
                c_src_file = c_src_file[lbf:]
                c_sources_list.append(c_src_file)
                c_sources += ' \\\n  ' + c_src_file


    for koren, subFolders, files in os.walk(fulldir):
        for subor in files:
            if ".a" in subor:
                if "GCC" in subor:
                    lib_sources += ' \\\n  ' + subor

# MCU
mcu = ''
#node = root.find('.//toolChain[@superClass="fr.ac6.managedbuild.toolchain.gnu.cross.exe.release"]/option[@name="Mcu"]')
node = root.find('.//toolChain[@superClass="fr.ac6.managedbuild.toolchain.gnu.cross.exe.debug"]/option[@name="Mcu"]')

try:
    value = node.attrib.get('value')
except Exception, e:
    sys.stderr.write("No target MCU defined\r\n")
    sys.exit(C2M_ERR_PROJECT_FILE)
#print mcu_cflags.items()
for pattern, option in mcu_cflags.items():
    if pattern.match(value):
        mcu = option
if (mcu == ''):
    sys.stderr.write("Unknown MCU\r\n, please contact author for an update of this utility\r\n")
    sys.stderr.exit(C2M_ERR_NEED_UPDATE)
print "MCU:\t\t\t", mcu
# AS include
as_includes = 'AS_INCLUDES ='

#TrueStudio
#nodes = root.findall('.//tool[@superClass="com.atollic.truestudio.exe.debug.toolchain.as"]/option[@valueType="includePath"]/listOptionValue')
#SW4STM32
#nodes = root.findall('.//toolChain[@superClass="fr.ac6.managedbuild.toolchain.gnu.cross.exe.release"]/tool[@superClass="fr.ac6.managedbuild.tool.gnu.cross.assembler"]/option[@valueType="includePath"]/listOptionValue')
nodes = root.findall('.//toolChain[@superClass="fr.ac6.managedbuild.toolchain.gnu.cross.exe.debug"]/tool[@superClass="fr.ac6.managedbuild.tool.gnu.cross.assembler"]/option[@valueType="includePath"]/listOptionValue')
first = 1
for node in nodes:
    value = node.attrib.get('value')
    if (value != ""):
        value = re.sub(r'^..(\\|/)..(\\|/)..(\\|/)', '', value.replace('\\', os.path.sep))
        if first:
            as_includes = 'AS_INCLUDES = -I' + value
            first = 0
        else:
            as_includes += '\nAS_INCLUDES += -I' + value
# AS symbols
#print as_includes
as_defs = 'AS_DEFS ='

#nodes = root.findall('.//toolChain[@superClass="fr.ac6.managedbuild.toolchain.gnu.cross.exe.release"]/tool[@superClass="fr.ac6.managedbuild.tool.gnu.cross.assembler"]/option[@valueType="definedSymbols"]/listOptionValue')
nodes = root.findall('.//toolChain[@superClass="fr.ac6.managedbuild.toolchain.gnu.cross.exe.debug"]/tool[@superClass="fr.ac6.managedbuild.tool.gnu.cross.assembler"]/option[@valueType="definedSymbols"]/listOptionValue')
for node in nodes:
    value = node.attrib.get('value')
    if (value != ""):
        as_defs += ' -D' + value
#print as_defs
# C include
c_includes = 'C_INCLUDES ='
#nodes = root.findall('.//toolChain[@superClass="fr.ac6.managedbuild.toolchain.gnu.cross.exe.release"]/tool[@superClass="fr.ac6.managedbuild.tool.gnu.cross.c.compiler"]/option[@valueType="includePath"]/listOptionValue')
nodes = root.findall('.//toolChain[@superClass="fr.ac6.managedbuild.toolchain.gnu.cross.exe.debug"]/tool[@superClass="fr.ac6.managedbuild.tool.gnu.cross.c.compiler"]/option[@valueType="includePath"]/listOptionValue')

first = 1
for node in nodes:
    value = node.attrib.get('value')
    # delete pattern '..\' from beginging of path
    while value.find("..\\")>=0:
        value = value[3:]
    if (value != ""):
        value = re.sub(r'^..(\\|/)..(\\|/)..(\\|/)', '', value.replace('\\', os.path.sep))
        if first:
            c_includes = 'C_INCLUDES = -I' + value
            first = 0
        else:
            c_includes += '\nC_INCLUDES += -I' + value

hdirs = set()
fulldir=os.path.join(proj_folder,"Middlewares")
if os.path.exists(fulldir):
    #print "---MIDDLEWARE----Headers-----"
    for koren, subFolders, files in os.walk(fulldir):
        for subor in files:
            extension = subor.split('.')[1]
            if extension == "h":
                h_dir = koren[lbf:]
                hdirs.add(h_dir)
                sbr = os.path.join(koren,subor)
                subor = sbr[lbf:]
                c_sources_list.append(subor)
                #break

    for hdir in hdirs:
        c_includes += '\nC_INCLUDES += -I' + hdir
        #print hdir

fulldir=os.path.join(proj_folder,"Drivers")
fulldir=os.path.join(fulldir,"BSP")
hdirs = set()
if os.path.exists(fulldir):
    lbf = len(proj_folder)+1
    for koren, subFolders, files in os.walk(fulldir):
        for subor in files:
            extension = subor.split('.')[1]
            if extension == "h":
                h_dir = koren[lbf:]
                hdirs.add(h_dir)
                sbr = os.path.join(koren,subor)
                subor = sbr[lbf:]
                c_sources_list.append(subor)

                #c_src_file = os.path.join(koren,subor)
                #c_src_file = c_src_file[lbf:]
                #hdirs.add(h_dir)
                #c_sources_list.append(c_src_file)
                #c_sources += ' \\\n  ' + c_src_file
    for hdir in hdirs:
        c_includes += '\nC_INCLUDES += -I' + hdir
        print hdir

#print c_includes
# C symbols
c_defs = 'C_DEFS = '
#                                                                            nodes = root.findall('.//tool[@superClass="com.atollic.truestudio.exe.debug.toolchain.gcc"]/option[@valueType="definedSymbols"]/listOptionValue')
#nodes = root.findall('.//toolChain[@superClass="fr.ac6.managedbuild.toolchain.gnu.cross.exe.release"]/tool[@superClass="fr.ac6.managedbuild.tool.gnu.cross.c.compiler"]/option[@valueType="definedSymbols"]/listOptionValue')
nodes = root.findall('.//toolChain[@superClass="fr.ac6.managedbuild.toolchain.gnu.cross.exe.debug"]/tool[@superClass="fr.ac6.managedbuild.tool.gnu.cross.c.compiler"]/option[@valueType="definedSymbols"]/listOptionValue')
for node in nodes:
    value = node.attrib.get('value')
    if (value != ""):
        if value.find("=")>=0:
            casti = value.split("=")
            if casti[0] in c_defs and casti[1] in c_defs:
                continue
            # determine if C_DEFS parameters are encloed in '"'
            if casti[1][0]!='\"':
                value  = casti[0]+'=\"'+casti[1]+'\"'
        c_defs += ' -D' + value
#print c_defs
# Link script
memory = ''
estack = ''
#nodes = root.findall('.//toolChain[@superClass="fr.ac6.managedbuild.toolchain.gnu.cross.exe.release"]/tool[@superClass="fr.ac6.managedbuild.tool.gnu.cross.c.linker"]/option[@superClass="fr.ac6.managedbuild.tool.gnu.cross.c.linker.script"]')
nodes = root.findall('.//toolChain[@superClass="fr.ac6.managedbuild.toolchain.gnu.cross.exe.debug"]/tool[@superClass="fr.ac6.managedbuild.tool.gnu.cross.c.linker"]/option[@superClass="fr.ac6.managedbuild.tool.gnu.cross.c.linker.script"]')
node=nodes[0]
ldscript = node.attrib.get("value")
try:
	ldscript = ldscript.split("\\")[1]
except IndexError, ex:
	ldscript = ldscript.split("/")[1]
#ld_script = "\""+proj_folder +"/SW4STM32/"+proj_name+" Configuration/"+ldscript+"\""
ld_script = "\""+proj_folder_rel_path + os.path.sep + ldscript+"\""
#print "LD_SCRIPT=", ld_script

mf = mft.substitute( \
    GCC_PATH_VAR = localSetting["GCC_PATH"], \
    FLASH_PATH_VAR = localSetting["FLASH_PATH"], \
    TARGET = proj_name, \
    MCU = mcu, \
    C_SOURCES = c_sources, \
    ASM_SOURCES = asm_sources, \
    AS_DEFS = as_defs, \
    AS_INCLUDES = as_includes, \
    C_DEFS = c_defs, \
    LD_SCRIPT = ld_script, \
    C_INCLUDES = c_includes,\
    CODE_OPTIMALIZATION = flag_opt)

try:
    fd = open(proj_folder + os.path.sep + 'Makefile', 'wb')
    fd.write(mf)
    fd.close()
except:
    sys.stderr.write("Write Makefile failed\r\n")
    sys.exit(C2M_ERR_IO)

sys.stdout.write("File created: %s\r\n" % (proj_folder + os.path.sep + 'Makefile'))
p = subprocess.Popen("arm-none-eabi-gcc -dumpversion", stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
if output[0] == "4":
    sys.stdout.write("----------------------------------------------------------------------------\n")
#    sys.stdout.write("Note:\tTo get better performance use gcc v.5!\n")
'''
ld = ldt.substitute( \
    MEMORY = memory, \
    ESTACK = estack)
try:
    fd = open(proj_folder + os.path.sep + 'arm-gcc-link.ld', 'wb')
    fd.write(ld)
    fd.close()
except:
    sys.stderr.write("Write link script failed\r\n")
    sys.exit(C2M_ERR_IO)
sys.stdout.write("File created: %s\r\n" % (proj_folder + os.path.sep + 'arm-gcc-link.ld'))
'''

#nodes = root.findall('.//toolChain[@superClass="fr.ac6.managedbuild.toolchain.gnu.cross.exe.release"]/tool[@superClass="fr.ac6.managedbuild.tool.gnu.cross.c.compiler"]/option[@valueType="includePath"]/listOptionValue')
nodes = root.findall('.//toolChain[@superClass="fr.ac6.managedbuild.toolchain.gnu.cross.exe.debug"]/tool[@superClass="fr.ac6.managedbuild.tool.gnu.cross.c.compiler"]/option[@valueType="includePath"]/listOptionValue')
inc_files=[]
for node in nodes:
    value = node.attrib.get('value')
    while value.find("../") >= 0:
        value = value[3:]
    if (value != ""):
        inc_files.append(value)

try:
    fd = open(proj_folder + os.path.sep + proj_name + ".cbp", 'w')
    fd.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n')
    fd.write('<CodeBlocks_project_file>\n')
    fd.write('<FileVersion major="1" minor="6" />\n')
    fd.write('<Project>\n')
    fd.write('<Option title="'+proj_name+'" />\n')
    fd.write('<Option makefile_is_custom="1" />\n')
    fd.write('<Option pch_mode="2" />\n')
    fd.write('<Option compiler="arm-elf-gcc" />\n')
    fd.write('<MakeCommands>\n')
    fd.write('\t<Build command="$make -f $makefile $target" />\n')
    fd.write('\t<CompileFile command="$make -f $makefile $file" />\n')
    fd.write('\t<Clean command="$make -f $makefile clean$target" />\n')
    fd.write('\t<DistClean command="$make -f $makefile distclean$target" />\n')
    fd.write('\t<AskRebuildNeeded command="$make -f $makefile flash" />\n')
    fd.write('\t<SilentBuild command="$make -f $makefile $target &gt; $(CMD_NULL)" />\n')
    fd.write('</MakeCommands>\n')
    fd.write('<Build>\n')
    fd.write('\t<Target title="Debug">\n')
    '''
    fd.write('\t\t<Option output="bin" prefix_auto="1" extension_auto="1" />\n')
    fd.write('\t\t<Option object_output="obj/Debug/" />\n')
    fd.write('\t\t<Option type="1" />\n')
    fd.write('\t\t<Option compiler="arm-elf-gcc" />\n')
    fd.write('\t\t<Compiler><Add option="-g" /></Compiler>\n')
    '''
    fd.write('\t</Target>\n')
    fd.write('\t<Target title="Release">\n')
    '''
    fd.write('\t\t<Option output="bin" prefix_auto="1" extension_auto="1" />\n')
    fd.write('\t\t<Option object_output="obj/Release/" />\n')
    fd.write('\t\t<Option type="1" />\n')
    fd.write('\t\t<Option compiler="arm-elf-gcc" />\n')
    fd.write('\t\t<Compiler><Add option="-g" /></Compiler>\n')
    '''
    fd.write('\t<MakeCommands>\n')
    fd.write('\t\t<Build command="$make -f $makefile $target" />\n')
    fd.write('\t\t<CompileFile command="$make -f $makefile $file" />\n')
    fd.write('\t\t<Clean command="$make -f $makefile clean$target" />\n')
    fd.write('\t\t<DistClean command="$make -f $makefile distclean$target" />\n')
    fd.write('\t\t<AskRebuildNeeded command="$make -f $makefile flash" />\n')
    fd.write('\t\t<SilentBuild command="$make -f $makefile $target &gt; $(CMD_NULL)" />\n')
    fd.write('\t</MakeCommands>\n')
    fd.write('\t</Target>\n')
    fd.write('</Build>\n')
    fd.write('\n')

    abp = sys.argv[1] #os.path.abspath(os.curdir)
    for inc_file in inc_files:
        # delete pattern '..\' from beginging of path
        while inc_file.find("..\\")>=0:
            inc_file = inc_file[3:]
        #convert '\' -> '/' (linux like)
        inc_file = re.sub(r'^..(\\|/)..(\\|/)..(\\|/)', '', inc_file.replace('\\', os.path.sep))
        for name in os.listdir(os.path.join(proj_folder, inc_file)):
            isf = abp+os.path.sep+inc_file+os.path.sep+name
            if os.path.isfile(isf):
                fd.write('<Unit filename="'+inc_file+os.path.sep+name+'"/>\n')

    inc_filesX = "Drivers/STM32F0xx_HAL_Driver/Src/"
    for name in c_sources_list:
        #print "write", name
        fd.write('<Unit filename="'+name+'"><Option compilerVar="CC" /></Unit>\n')
    #debugger session
    fd.write('<Extensions>\n')
    fd.write('<envvars />\n')
    fd.write('<code_completion />\n')
    fd.write('<debugger>\n')
    fd.write('  <search_path add="./build" />\n')
    fd.write('  <remote_debugging>\n')
    fd.write('      <options conn_type="0" serial_baud="115200" ip_address="%s" ip_port="%s" additional_cmds="reset" />\n'%(localSetting["GDP_IP_ADDRESS"], localSetting["GDB_IP_PORT"]))
    fd.write('  </remote_debugging>\n')
    fd.write('  <remote_debugging target="Debug">\n')
    fd.write('      <options conn_type="0" serial_baud="115200" ip_address="%s" ip_port="%s" additional_cmds="monitor reset init&#x0A;monitor halt&#x0A;monitor soft_reset_halt&#x0A;'%(localSetting["GDP_IP_ADDRESS"], localSetting["GDB_IP_PORT"]))
    fd.write('file ./build/'+proj_name+'.elf&#x0A;load&#x0A;monitor_soft_reset_halt" extended_remote="1" />\n')
    fd.write('  </remote_debugging>\n')
    fd.write('</debugger>\n')
    fd.write('<lib_finder disable_auto="1" />\n')
    fd.write('</Extensions>\n')

    fd.write('</Project>\n')
    fd.write('</CodeBlocks_project_file>\n')
    fd.close()
except Exception, e:
    print e
    sys.stderr.write("Write Code::Block project failed\r\n")
    sys.exit(C2M_ERR_IO)
sys.exit(C2M_ERR_SUCCESS)
