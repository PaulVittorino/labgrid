from labgrid.resource.udev import JLinkDevice

FAKE_SERIAL = 123456

def test_jlink_resource(target):
    r = JLinkDevice(
        target, name=None, match={"ID_SERIAL_SHORT": f"000000{FAKE_SERIAL}"}
    )
