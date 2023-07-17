from random import choice
import numpy as np
import os
from PIL import Image
from stego_lsb.bit_manipulation import roundup
from stego_lsb.LSBSteg import hide_data, recover_data
import string
import unittest


class TestLSBSteg(unittest.TestCase):
    def write_random_image(self, filename: str, width: int, height: int, num_channels: int) -> None:
        image_data = np.random.randint(0, 256, size=(height, width, num_channels), dtype=np.uint8)
        image = Image.fromarray(image_data)
        image.save(filename)

    def write_random_file(self, filename: str, num_bytes: int) -> None:
        with open(filename, "wb") as file:
            file.write(os.urandom(num_bytes))

    def check_random_interleaving(self, num_trials: int = 256, filename_length: int = 5, num_channels: int = 3) -> None:
        filename = "".join(choice(string.ascii_lowercase) for _ in range(filename_length))
        png_input_filename = f"{filename}.png"
        payload_input_filename = f"{filename}.txt"
        png_output_filename = f"{filename}_steg.png"
        payload_output_filename = f"{filename}_recovered.txt"

        np.random.seed(0)
        for _ in range(num_trials):
            width = np.random.randint(1, 256)
            height = np.random.randint(1, 256)
            num_lsb = np.random.randint(1, 9)

            file_size_tag_length = roundup(int(num_channels * width * height * num_lsb).bit_length() / 8)
            payload_len = (num_channels * width * height * num_lsb - 8 * file_size_tag_length) // 8

            if payload_len < 0:
                continue

            self.write_random_image(png_input_filename, width=width, height=height, num_channels=num_channels)
            self.write_random_file(payload_input_filename, num_bytes=payload_len)

            try:
                hide_data(png_input_filename, payload_input_filename, png_output_filename, num_lsb, compression_level=1)
                recover_data(png_output_filename, payload_output_filename, num_lsb)
            except ValueError as e:
                os.remove(png_input_filename)
                os.remove(payload_input_filename)
                os.remove(png_output_filename)
                os.remove(payload_output_filename)
                raise e

            with open(payload_input_filename, "rb") as input_file, open(payload_output_filename, "rb") as output_file:
                input_payload_data = input_file.read()
                output_payload_data = output_file.read()

            os.remove(png_input_filename)
            os.remove(payload_input_filename)
            os.remove(png_output_filename)
            os.remove(payload_output_filename)

            self.assertEqual(input_payload_data, output_payload_data)

    def test_rgb_steganography_consistency(self) -> None:
        self.check_random_interleaving(num_channels=3)

    def test_rgba_steganography_consistency(self) -> None:
        self.check_random_interleaving(num_channels=4)

    def test_la_steganography_consistency(self) -> None:
        self.check_random_interleaving(num_channels=2)


if __name__ == "__main__":
    unittest.main()
