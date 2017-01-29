# https://zenpack-sdk.zenoss.com/en/2.0.0/changes.html
from ZenPacks.zenoss.ZenPackLib import zenpacklib
CFG = zenpacklib.load_yaml()
schema = CFG.zenpack_module.schema
