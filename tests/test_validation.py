from qreader.exceptions import QrCorruptError
from qreader.validation import validate_format_info, format_info_check
from tests.helpers import TestCase

__author__ = 'ewino'


class TestFormatInfoValidation(TestCase):
    def test_valid_format_info(self):
        samples = [
            0b010001111010110,  # L0
            0b011001000111101,  # L4
            0b000111101011001,  # M3
            0b001101110000101,  # M6
            0b110101100100011,  # Q2
            0b111010110010001,  # Q5
            0b100011110101100,  # H1
            0b101110000101001,  # H7
        ]
        for sample in samples:
            self.assertEqual(0, format_info_check(sample))

    def test_invalid_format_info(self):
        single_bit_error = [
            0b010011111010110,  # L0
            0b011001010111101,  # L4
            0b000111001011001,  # M3
            0b001100110000101,  # M6
        ]
        double_bit_error = [
            0b110101101000011,  # Q2
            0b111110110011001,  # Q5
            0b101011110001100,  # H1
            0b111110000111001,  # H7
        ]
        triple_bit_error = [
            0b110101101000010,  # Q2
            0b111110110011000,  # Q5
            0b101011110001101,  # H1
            0b111110000111000,  # H7
        ]

        for sample in single_bit_error + double_bit_error + triple_bit_error:
            self.assertNotEqual(0, format_info_check(sample))


class TestFormatInfoErrorCorrection(TestCase):
    def test_validate_format_info(self):
        samples = [
            0b010001111010110,  # L0
            0b011001000111101,  # L4
            0b000111101011001,  # M3
            0b001101110000101,  # M6
            0b110101100100011,  # Q2
            0b111010110010001,  # Q5
            0b100011110101100,  # H1
            0b101110000101001,  # H7
        ]

        for sample in samples:
            self.assertEqual(sample >> 10, validate_format_info(sample))

    def test_validate_erroneous_format_info(self):
        single_bit_error = [
            (0b010011111010110, 0b01000),  # L0
            (0b011001010111101, 0b01100),  # L4
            (0b000111001011001, 0b00011),  # M3
            (0b001100110000101, 0b00110),  # M6
        ]
        double_bit_error = [
            (0b110101101000011, 0b11010),  # Q2
            (0b111110110011001, 0b11101),  # Q5
            (0b101011110001100, 0b10001),  # H1
            (0b111110000111001, 0b10111),  # H7
        ]
        triple_bit_error = [
            (0b110101101000010, 0b11010),  # Q2
            (0b111110110011000, 0b11101),  # Q5
            (0b101011110001101, 0b10001),  # H1
            (0b111110000111000, 0b10111),  # H7
        ]

        for sample, correct in single_bit_error + double_bit_error + triple_bit_error:
            self.assertEqual(correct, validate_format_info(sample))

    def test_completely_wrong_format_info(self):
        samples = [
            0b010001111010110,  # L0
            0b011001000111101,  # L4
            0b000111101011001,  # M3
            0b001101110000101,  # M6
            0b110101100100011,  # Q2
            0b111010110010001,  # Q5
            0b100011110101100,  # H1
            0b101110000101001,  # H7
        ]
        for sample in samples:
            self.assertNotEqual(sample >> 10, validate_format_info(sample ^ 0b111111000000000))

    def test_unsalvageable_format_info(self):
        sample = 0b010001111010110 ^ 0b000001111111111  # flip all error correction bits
        self.assertRaises(QrCorruptError, validate_format_info, sample)

    def test_dual_formats_one_right_one_wrong(self):
        samples = [
            0b010001111010110,  # L0
            0b011001000111101,  # L4
            0b000111101011001,  # M3
            0b001101110000101,  # M6
            0b110101100100011,  # Q2
            0b111010110010001,  # Q5
            0b100011110101100,  # H1
            0b101110000101001,  # H7
        ]
        for sample in samples:
            self.assertEqual(sample >> 10, validate_format_info(sample, sample))
            self.assertEqual(sample >> 10, validate_format_info(sample ^ 0b111100000000000, sample ^ 0b000100000011101))
