from labscript_devices import register_classes

register_classes(
    'IDSCamera',
    BLACS_tab='lics_labscript_devices.IDSCamera.blacs_tabs.IDSCameraTab',
    runviewer_parser=None,
)
