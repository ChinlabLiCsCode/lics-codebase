#####################################################################
#                                                                   #
# /LiCs_devices/Dp832/register_classes.py                           #
#                                                                   #
# This code is adapted from naqslab with modifications              #
# made to enable compatibility with the rigol DP832 power supply    #
#####################################################################
import labscript_devices

labscript_devices.register_classes(
    'DP832',
    BLACS_tab='LiCs_devices.DP832.blacs_tabs.DP832Tab',
    runviewer_parser='')