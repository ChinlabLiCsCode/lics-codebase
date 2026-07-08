from labscript_devices import register_classes

register_classes(
    'PCOCamera',
    BLACS_tab='lics_labscript_devices.PCOCamera.blacs_tabs.PCOCameraTab',
    runviewer_parser=None,
)
