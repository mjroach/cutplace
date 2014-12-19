"""
Tests for `cid` module
"""

# Copyright (C) 2009-2013 Thomas Aglassinger
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import unittest

from cutplace import checks
from cutplace import interface
from cutplace import data
from cutplace import errors
from cutplace import fields
from cutplace import ranges
from cutplace import iotools
from tests import dev_test


class CidTest(unittest.TestCase):

    """
    Tests for cid module
    """
    _TEST_ENCODING = "cp1252"

    def test_can_read_excel_and_create_data_format_delimited(self):
        cid_reader = interface.Cid()
        source_path = dev_test.path_to_test_cid("icd_customers.xls")
        print(source_path)
        cid_reader.read(source_path, iotools.excel_rows(source_path))

        self.assertEqual(cid_reader._data_format.format, "delimited")
        self.assertEqual(cid_reader._data_format.header, 1)

    def test_fails_on_empty_data_format_property_name(self):
        cid_reader = interface.Cid()
        self.assertRaises(errors.InterfaceError, cid_reader.read, 'inline', [
            ['d', 'format', 'delimited'],
            ['d', '', ''],
        ])

    def test_fails_on_missing_data_format_property_value(self):
        cid_reader = interface.Cid()
        self.assertRaises(errors.InterfaceError, cid_reader.read, 'inline', [
            ['d', 'format', 'delimited'],
            ['d', 'header'],
        ])

    def test_fails_on_missing_data_format_property_name(self):
        cid_reader = interface.Cid()
        self.assertRaises(errors.InterfaceError, cid_reader.read, 'inline', [
            ['d', 'format', 'delimited'],
            ['d'],
        ])

    def test_fails_on_invalid_row_typ(self):
        cid_reader = interface.Cid()
        self.assertRaises(errors.InterfaceError, cid_reader.read, 'inline', [['x']])

    def test_can_skip_empty_rows(self):
        cid_reader = interface.Cid()
        cid_reader.read('inline', [
            [],
            [''],
            ['d', 'format', 'delimited']])
        self.assertEqual(cid_reader._data_format.format, "delimited")

    def test_can_read_field_type_text_field(self):
        cid_reader = interface.Cid()
        cid_reader.read('inline', [
            ['d', 'format', 'delimited'],
            ['f', 'branch_id', '38000', '', '5']])
        self.assertEqual(cid_reader.field_names[0], 'branch_id')
        self.assertEqual(cid_reader.field_format_at(0).length.description, ranges.Range('5').description)

    def test_can_read_fields_from_excel(self):
        cid_reader = interface.Cid()
        source_path = dev_test.path_to_test_cid("icd_customers.xls")
        cid_reader.read(source_path, iotools.excel_rows(source_path))
        self.assertEqual(cid_reader.field_names[0], 'branch_id')
        self.assertEqual(cid_reader.field_format_at(0).length.items, ranges.Range('5').items)
        self.assertTrue(isinstance(cid_reader.field_format_at(0), fields.TextFieldFormat))
        self.assertEqual(cid_reader.field_names[1], 'customer_id')
        self.assertTrue(isinstance(cid_reader.field_format_at(1), fields.IntegerFieldFormat))
        self.assertEqual(cid_reader.field_format_at(1).length.items, ranges.Range('2...').items)
        self.assertEqual(cid_reader.field_names[2], 'first_name')
        self.assertTrue(isinstance(cid_reader.field_format_at(2), fields.TextFieldFormat))
        self.assertEqual(cid_reader.field_format_at(2).length.items, ranges.Range('...60').items)
        self.assertEqual(cid_reader.field_names[3], 'surname')
        self.assertTrue(isinstance(cid_reader.field_format_at(3), fields.TextFieldFormat))
        self.assertEqual(cid_reader.field_format_at(3).length.items, ranges.Range('...60').items)
        self.assertEqual(cid_reader.field_names[4], 'gender')
        self.assertTrue(isinstance(cid_reader.field_format_at(4), fields.ChoiceFieldFormat))
        self.assertEqual(cid_reader.field_format_at(4).length.items, ranges.Range('2...6').items)
        self.assertEqual(cid_reader.field_names[5], 'date_of_birth')
        self.assertTrue(isinstance(cid_reader.field_format_at(5), fields.DateTimeFieldFormat))
        self.assertTrue(cid_reader.field_format_at(5).is_allowed_to_be_empty)
        self.assertEqual(cid_reader.field_format_at(5).length.items, ranges.Range('10').items)

    def test_can_handle_all_field_formats_from_array(self):
        cid_reader = interface.Cid()
        cid_reader.read('inline', [
            ['d', 'format', 'delimited'],
            ['f', 'int', '', '', '', 'Integer'],
            ['f', 'choice', '', '', '', 'Choice', 'x,y'],
            ['f', 'date', '', '', '', 'DateTime'],
            ['f', 'dec', '', '', '', 'Decimal', ''],
            ['f', 'text']
        ])
        self.assertTrue(isinstance(cid_reader.field_format_at(0), fields.IntegerFieldFormat))
        self.assertTrue(isinstance(cid_reader.field_format_at(1), fields.ChoiceFieldFormat))
        self.assertTrue(isinstance(cid_reader.field_format_at(2), fields.DateTimeFieldFormat))
        self.assertTrue(isinstance(cid_reader.field_format_at(3), fields.DecimalFieldFormat))
        self.assertTrue(isinstance(cid_reader.field_format_at(4), fields.TextFieldFormat))

    def test_can_handle_all_field_formats_from_excel(self):
        cid_reader = interface.Cid()
        source_path = dev_test.path_to_test_cid("alltypes.xls")
        cid_reader.read(source_path, iotools.excel_rows(source_path))
        self.assertTrue(isinstance(cid_reader.field_format_at(0), fields.IntegerFieldFormat))
        self.assertTrue(isinstance(cid_reader.field_format_at(1), fields.TextFieldFormat))
        self.assertTrue(isinstance(cid_reader.field_format_at(2), fields.ChoiceFieldFormat))
        self.assertTrue(isinstance(cid_reader.field_format_at(3), fields.DateTimeFieldFormat))
        self.assertTrue(isinstance(cid_reader.field_format_at(4), fields.DecimalFieldFormat))

    def test_fails_on_empty_field_name(self):
        cid_to_read = interface.Cid()
        self.assertRaises(
            errors.InterfaceError, cid_to_read.read, 'inline', [
                ['d', 'format', 'delimited'],
                ['f', '', '38000', '', '5']
            ])

    def test_fails_on_numeric_field_name(self):
        cid_to_read = interface.Cid()
        self.assertRaises(
            errors.InterfaceError, cid_to_read.read, 'inline', [
                ['d', 'format', 'delimited'],
                ['f', '3', '38000', '', '5']
            ])

    def test_fails_on_special_character_as_field_name(self):
        cid_to_read = interface.Cid()
        self.assertRaises(
            errors.InterfaceError, cid_to_read.read, 'inline', [
                ['d', 'format', 'delimited'],
                ['f', '%', '38000', '', '5']
            ])

    def test_fails_on_python_keyword_as_field_name(self):
        cid_to_read = interface.Cid()
        self.assertRaises(
            errors.InterfaceError, cid_to_read.read, 'inline', [
                ['d', 'format', 'delimited'],
                ['f', 'class', '38000', '', '5']
            ])

    def test_can_read_delimited_rows(self):
        cid_reader = interface.Cid()
        source_path = dev_test.path_to_test_cid("icd_customers.xls")

        cid_reader.read(source_path, iotools.excel_rows(source_path))

        delimited_rows = iotools.delimited_rows(dev_test.path_to_test_data("valid_customers.csv"), cid_reader._data_format)

        for row in delimited_rows:
            delimited_row = row
            break

        self.assertEqual(delimited_row, ['38000', '23', 'John', 'Doe', 'male', '08.03.1957'])

    def test_can_handle_checks_from_excel(self):
        cid_reader = interface.Cid()
        source_path = dev_test.path_to_test_cid("customers.xls")
        cid_reader.read(source_path, iotools.excel_rows(source_path))
        self.assertTrue(isinstance(cid_reader.check_for(cid_reader.check_names[0]), checks.IsUniqueCheck))
        self.assertTrue(isinstance(cid_reader.check_for(cid_reader.check_names[1]), checks.DistinctCountCheck))

    def test_can_be_rendered_as_str(self):
        customers_cid_path = dev_test.path_to_test_cid("customers.xls")
        customers_cid = interface.Cid(customers_cid_path)
        cid_str = str(customers_cid)
        self.assertTrue('Cid' in cid_str)
        self.assertTrue(data.FORMAT_DELIMITED in cid_str)
        self.assertTrue(customers_cid.field_names[0] in cid_str)

    def _create_cid_from_string(self, cid_text):
        with io.StringIO(cid_text) as cid_string_io:
            result = interface.Cid(cid_string_io)
        return result

    def test_can_create_cid_from_text(self):
        cid_text = '\n'.join([
            ',Example CID as CSV from a string',
            'D,Format,%s' % data.FORMAT_DELIMITED,
            ' ,Name         ,,,Length,Type    ,Rule',
            'F,name         ,,,...50',
            'F,height       ,,,      ,Decimal',
            'F,date_of_birth,,,      ,DateTime,YYYY-MM-DD',
        ])
        cid_from_text = self._create_cid_from_string(cid_text)
        self.assertEqual(data.FORMAT_DELIMITED, cid_from_text.data_format.format)

    def test_fails_on_broken_cid_from_text(self):
        cid_text = '\n'.join([
            ',Example CID as CSV from a string',
            'D,Format,no_such_format',
        ])
        self.assertRaises(errors.InterfaceError, self._create_cid_from_string, cid_text)

    def test_fails_on_empty_cid_from_text(self):
        self.assertRaises(errors.InterfaceError, self._create_cid_from_string, '')


if __name__ == '__main__':
    unittest.main()
