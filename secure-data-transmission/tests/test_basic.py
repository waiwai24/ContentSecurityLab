import unittest
from src.channel.onenet_channel import OneNetChannel
from src.channel.other_channel import OtherChannel
from src.steganography.lsb import LSBSteganography
from src.steganography.dct import DCTSteganography
from src.fragmentation.fragmenter import Fragmenter
from src.fragmentation.reassembler import Reassembler
from src.sync.sync_mechanism import SyncMechanism

class TestBasicFunctionality(unittest.TestCase):

    def setUp(self):
        self.onenet_channel = OneNetChannel()
        self.other_channel = OtherChannel()
        self.lsb_steganography = LSBSteganography()
        self.dct_steganography = DCTSteganography()
        self.fragmenter = Fragmenter()
        self.reassembler = Reassembler()
        self.sync_mechanism = SyncMechanism()

    def test_onenet_channel(self):
        self.assertTrue(self.onenet_channel.establish_channel())
        self.assertTrue(self.onenet_channel.send_data("Test data"))
        received_data = self.onenet_channel.receive_data()
        self.assertEqual(received_data, "Test data")

    def test_other_channel(self):
        self.assertTrue(self.other_channel.establish_channel())
        self.assertTrue(self.other_channel.send_data("Test data"))
        received_data = self.other_channel.receive_data()
        self.assertEqual(received_data, "Test data")

    def test_lsb_steganography(self):
        image = "test_image.png"
        payload = "Secret Message"
        self.lsb_steganography.hide_data(image, payload, color_channels=3, lsb_count=1)
        extracted_data = self.lsb_steganography.extract_data(image)
        self.assertEqual(extracted_data, payload)

    def test_dct_steganography(self):
        image = "test_image.png"
        payload = "Secret Message"
        self.dct_steganography.hide_data(image, payload, color_channels=3, pixel_pairs=5)
        extracted_data = self.dct_steganography.extract_data(image)
        self.assertEqual(extracted_data, payload)

    def test_fragmentation(self):
        data = "This is a test message that needs to be fragmented."
        fragments = self.fragmenter.fragment_data(data, num_fragments=2)
        self.assertEqual(len(fragments), 2)
        reassembled_data = self.reassembler.reassemble_data(fragments)
        self.assertEqual(reassembled_data, data)

    def test_sync_mechanism(self):
        self.sync_mechanism.set_sync_message("Ready to receive")
        self.assertEqual(self.sync_mechanism.get_sync_message(), "Ready to receive")

if __name__ == '__main__':
    unittest.main()