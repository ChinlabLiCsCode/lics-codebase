#####################################################################
#                                                                   #
# /LiCs_devices/VISA/register_classes.py                            #
#                                                                   #
# This code is adapted from naqslab with modifications              #
# made to enable compatibility with the rigol DP832 power supply    #
#####################################################################
"""
Sets which BLACS_tab belongs to each labscript device.
"""

import labscript_devices

labscript_devices.register_classes(
    'VISA',
    BLACS_tab='LiCs_devices.VISA.blacs_tab.VISATab',
    runviewer_parser=''
)
