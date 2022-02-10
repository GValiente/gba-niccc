#---------------------------------------------------------------------------------------------------------------------
# TARGET is the name of the output
# BUILD is the directory where object files & intermediate files will be placed
# LIBBUTANO is the main directory of butano library (https://github.com/GValiente/butano)
# PYTHON is the path to the python interpreter
# SOURCES is a list of directories containing source code
# INCLUDES is a list of directories containing extra header files
# DATA is a list of directories containing binary data
# GRAPHICS is a list of directories containing files to be processed by grit
# AUDIO is a list of directories containing files to be processed by mmutil
# USERFLAGS is a list of additional compiler flags:
#     Pass -flto to enable link-time optimization
#     Pass -O0 to improve debugging
#
# All directories are specified relative to the project directory where the makefile is found
#---------------------------------------------------------------------------------------------------------------------
TARGET      :=  $(notdir $(CURDIR))
BUILD       :=  build
LIBBUTANO   :=  ../butano/butano
PYTHON      :=  python
SOURCES     :=  src data
INCLUDES    :=  include
DATA        :=
GRAPHICS    :=  graphics
AUDIO       :=  audio
USERFLAGS   :=  -DBN_CFG_AUDIO_MAX_MUSIC_CHANNELS=4 -DBN_CFG_AUDIO_MAX_SOUND_CHANNELS=1

#---------------------------------------------------------------------------------------------------------------------
# Export absolute butano path
#---------------------------------------------------------------------------------------------------------------------
ifndef LIBBUTANOABS
	export LIBBUTANOABS	:=	$(realpath $(LIBBUTANO))
endif

#---------------------------------------------------------------------------------------------------------------------
# Include main makefile
#---------------------------------------------------------------------------------------------------------------------
include $(LIBBUTANOABS)/butano.mak
