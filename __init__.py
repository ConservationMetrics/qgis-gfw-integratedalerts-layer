def classFactory(iface):
    from .gfw_controller_plugin import GFWControllerPlugin
    return GFWControllerPlugin(iface)
