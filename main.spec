# -*- mode: python ; coding: utf-8 -*-
import os
import face_recognition_models

# Get the path to face_recognition_models
models_path = os.path.dirname(face_recognition_models.face_recognition_model_location())

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include face recognition model files
        (models_path, 'face_recognition_models/models'),
        # Include app data directories
        ('app/data', 'app/data'),
        ('config', 'config'),
    ],
    hiddenimports=[
        'face_recognition',
        'face_recognition_models',
        'dlib',
        'cv2',
        'numpy',
        'PIL',
        'flask',
        'requests',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
