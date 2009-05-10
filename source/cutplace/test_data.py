"""
Tests for data formats.
"""
import data
import logging
import unittest

class DataFormatTest(unittest.TestCase):
    """
    Tests for data formats.
    """
    _TEST_ENCODING = "ascii"

    def testBasics(self):
        for formatName in [data.FORMAT_CSV, data.FORMAT_DELIMITED, data.FORMAT_FIXED]:
            format = data.createDataFormat(formatName)
            self.assertTrue(format)
            
    def testCsvDataFormat(self):
        format = data.CsvDataFormat()
        self.assertTrue(format.name)

        format.set(data.KEY_ENCODING, DataFormatTest._TEST_ENCODING)
        self.assertEqual(format.get(data.KEY_ENCODING).name.lower() , DataFormatTest._TEST_ENCODING)

        self.assertEqual(format.get(data.KEY_LINE_DELIMITER), data.ANY)
        self.assertEqual(format.get(data.KEY_ITEM_DELIMITER), data.ANY)
        self.assertEqual(format.get(data.KEY_QUOTE_CHARACTER), "\"")
        self.assertEqual(format.get(data.KEY_ESCAPE_CHARACTER), "\"")
        format.validateAllRequiredPropertiesHaveBeenSet()
        
    def testDelimitedDataFormat(self):
        format = data.DelimitedDataFormat()
        self.assertTrue(format.name)
        self.assertRaises(data.DataFormatSyntaxError, format.validateAllRequiredPropertiesHaveBeenSet)

        formatWithCr = data.DelimitedDataFormat()
        formatWithCr.set(data.KEY_LINE_DELIMITER, data.CR)
        self.assertEqual(formatWithCr.get(data.KEY_LINE_DELIMITER), "\r")
        
    def testBrokenEncoding(self):
        format = data.CsvDataFormat()
        self.assertRaises(data.DataFormatSyntaxError, format.set, data.KEY_ENCODING, "me-no-encoding")
        
if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger("cutplace.test_data").setLevel(logging.INFO)
    unittest.main()
