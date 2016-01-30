from qreader.constants import MODE_SIZE_SMALL, MODE_SIZE_MEDIUM, MODE_SIZE_LARGE, MODE_KANJI, MODE_ALPHA_NUM, \
    MODE_NUMBER, MODE_BYTES
from qreader.exceptions import IllegalQrVersionError, QrFormatError
from qreader.spec import get_mask_func, mode_sizes_for_version, bits_for_length, get_dead_zones, DATA_BLOCKS_INFO
from tests.helpers import TestCase

__author__ = 'ewino'


class TestMasks(TestCase):
    def test_mask_bounds(self):
        for mask_id in range(8):
            mask_func = get_mask_func(mask_id)
            for i in range(177):
                for j in range(177):
                    self.assertIn(mask_func(i, j), (0, 1))

    def test_nonexistent_masks(self):
        self.assertRaisesMsg(QrFormatError, lambda: get_mask_func(-1), 'Bad mask pattern: -1')
        self.assertRaisesMsg(QrFormatError, lambda: get_mask_func(8), 'Bad mask pattern: 8')

    def test_mask_formula_correctness(self):
        mask_samples = {
            0: '1010101010101010101010101010101010101010101010101',
            1: '1111111000000011111110000000111111100000001111111',
            2: '1001001100100110010011001001100100110010011001001',
            3: '1001001001001001001001001001001001001001001001001',
            4: '1110001111000100011100001110111000111100010001110',
            5: '1111111100000110010011010101100100110000011111111',
            6: '1111111111000111011011010101101101110001111111111',
            7: '1010101000111010001110101010111000101110001010101',
        }

        for mask_id in range(8):
            mask_func = get_mask_func(mask_id)
            mask_result = ''
            for i in range(7):
                for j in range(7):
                    mask_result += '1' if mask_func(i, j) else '0'
            self.assertEqual(mask_samples[mask_id], mask_result)


class TestCharCounts(TestCase):

    def test_size_for_version(self):
        self.assertEqual(MODE_SIZE_SMALL, mode_sizes_for_version(1))
        self.assertEqual(MODE_SIZE_SMALL, mode_sizes_for_version(2))
        self.assertEqual(MODE_SIZE_SMALL, mode_sizes_for_version(5))
        self.assertEqual(MODE_SIZE_SMALL, mode_sizes_for_version(9))
        self.assertEqual(MODE_SIZE_MEDIUM, mode_sizes_for_version(10))
        self.assertEqual(MODE_SIZE_MEDIUM, mode_sizes_for_version(11))
        self.assertEqual(MODE_SIZE_MEDIUM, mode_sizes_for_version(12))
        self.assertEqual(MODE_SIZE_MEDIUM, mode_sizes_for_version(20))
        self.assertEqual(MODE_SIZE_MEDIUM, mode_sizes_for_version(26))
        self.assertEqual(MODE_SIZE_LARGE, mode_sizes_for_version(27))
        self.assertEqual(MODE_SIZE_LARGE, mode_sizes_for_version(28))
        self.assertEqual(MODE_SIZE_LARGE, mode_sizes_for_version(39))
        self.assertEqual(MODE_SIZE_LARGE, mode_sizes_for_version(40))

    def test_size_for_illegal_versions(self):
        self.assertRaises(IllegalQrVersionError, lambda: mode_sizes_for_version(0))
        self.assertRaises(IllegalQrVersionError, lambda: mode_sizes_for_version(-1))
        self.assertRaises(IllegalQrVersionError, lambda: mode_sizes_for_version(41))
        self.assertRaises(IllegalQrVersionError, lambda: mode_sizes_for_version(0.5))
        self.assertRaises(IllegalQrVersionError, lambda: mode_sizes_for_version(-1.5))
        self.assertRaises(IllegalQrVersionError, lambda: mode_sizes_for_version(10.5))
        self.assertRaises(IllegalQrVersionError, lambda: mode_sizes_for_version(9.5))
        self.assertRaises(IllegalQrVersionError, lambda: mode_sizes_for_version(40.5))

    def test_char_counts(self):
        self.assertEqual(8, bits_for_length(8, MODE_KANJI))
        self.assertEqual(9, bits_for_length(8, MODE_ALPHA_NUM))
        self.assertEqual(10, bits_for_length(8, MODE_NUMBER))

        self.assertEqual(10, bits_for_length(18, MODE_KANJI))
        self.assertEqual(11, bits_for_length(18, MODE_ALPHA_NUM))
        self.assertEqual(12, bits_for_length(18, MODE_NUMBER))

        self.assertEqual(12, bits_for_length(28, MODE_KANJI))
        self.assertEqual(13, bits_for_length(28, MODE_ALPHA_NUM))
        self.assertEqual(14, bits_for_length(28, MODE_NUMBER))

        self.assertEqual(8, bits_for_length(8, MODE_BYTES))
        self.assertEqual(16, bits_for_length(18, MODE_BYTES))
        self.assertEqual(16, bits_for_length(28, MODE_BYTES))

    def test_illegal_char_counts(self):
        # illegal version
        self.assertRaises(IllegalQrVersionError, lambda: bits_for_length(0, 1))
        self.assertRaises(IllegalQrVersionError, lambda: bits_for_length(41, 1))
        self.assertRaises(IllegalQrVersionError, lambda: bits_for_length(8.5, 1))

        # illegal modes
        self.assertRaisesMsg(QrFormatError, lambda: bits_for_length(8, 0), 'Unknown data type ID: 0')
        self.assertRaisesMsg(QrFormatError, lambda: bits_for_length(8, -1), 'Unknown data type ID: -1')
        self.assertRaisesMsg(QrFormatError, lambda: bits_for_length(8, 3), 'Unknown data type ID: 3')
        self.assertRaisesMsg(QrFormatError, lambda: bits_for_length(8, 7), 'Unknown data type ID: 7')
        self.assertRaisesMsg(QrFormatError, lambda: bits_for_length(8, 9), 'Unknown data type ID: 9')

        # downright weird modes
        self.assertRaisesMsg(QrFormatError, lambda: bits_for_length(8, 3.5), 'Unknown data type ID: 3.5')
        self.assertRaisesMsg(QrFormatError, lambda: bits_for_length(8, None), 'Unknown data type ID: None')
        self.assertRaisesMsg(QrFormatError, lambda: bits_for_length(8, 'hi'), "Unknown data type ID: 'hi'")


class TestDeadZones(TestCase):
    REGULAR_ZONES_COUNT = 6

    def test_normal_dead_zones(self):
        self.assertEqual(self.REGULAR_ZONES_COUNT, len(get_dead_zones(1)))

    def test_alignment_patterns_amount(self):
        amounts = sum(([p**2] * x for p, x in enumerate([1, 5, 7, 7, 7, 7, 6])), [])  # 1*0, 5*1, 7*9, 7*16, 7*25...
        self.assertEqual(40, len(amounts))
        for version, amount in enumerate(amounts, start=1):
            regular_zones_count = self.REGULAR_ZONES_COUNT + (2 if version >= 7 else 0)
            self.assertEqual(amount, len(get_dead_zones(version)) - regular_zones_count)

    def test_illegal_versions(self):
        self.assertRaises(IllegalQrVersionError, lambda: get_dead_zones(-1))
        self.assertRaises(IllegalQrVersionError, lambda: get_dead_zones(0))
        self.assertRaises(IllegalQrVersionError, lambda: get_dead_zones(1.5))
        self.assertRaises(IllegalQrVersionError, lambda: get_dead_zones(41))


class TestBlockInfo(TestCase):

    def test_data_structure(self):
        self.assertEqual(40, len(DATA_BLOCKS_INFO))
        for version, ec_levels_info in enumerate(DATA_BLOCKS_INFO, start=1):
            self.assertEqual(4, len(ec_levels_info))
            for ec_level, data in enumerate(ec_levels_info):
                self.assertIsInstance(data, tuple)
                self.assertIn(len(data), (3, 4))
                for datum in data:
                    self.assertIsInstance(datum, int)

    def test_data_amount_consistent_per_version(self):
        for version, ec_levels_info in enumerate(DATA_BLOCKS_INFO, start=1):
            data_amounts = set()
            for level_info in ec_levels_info:
                amount = (level_info[0] + level_info[1]) * level_info[2]
                if len(level_info) > 3:
                    amount += (level_info[0] + level_info[1] + 1) * level_info[3]
                data_amounts.add(amount)
            self.assertEqual(1, len(data_amounts))
