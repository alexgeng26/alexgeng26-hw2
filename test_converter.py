"""
Comprehensive test suite for the Numeric Converter application.
Tests all input/output type combinations and error handling.
"""

import pytest
import base64
import json
from api.index import (
    text_to_number, 
    number_to_text, 
    base64_to_number, 
    number_to_base64,
    app
)


class TestTextToNumber:
    """Test text to number conversion functionality."""
    
    def test_single_digits(self):
        """Test conversion of single digit words."""
        assert text_to_number("one") == 1
        assert text_to_number("two") == 2
        assert text_to_number("three") == 3
        assert text_to_number("four") == 4
        assert text_to_number("five") == 5
        assert text_to_number("six") == 6
        assert text_to_number("seven") == 7
        assert text_to_number("eight") == 8
        assert text_to_number("nine") == 9
        assert text_to_number("ten") == 10
    
    def test_zero_variations(self):
        """Test zero variations."""
        assert text_to_number("zero") == 0
        assert text_to_number("nil") == 0
    
    def test_case_insensitive(self):
        """Test case insensitive conversion."""
        assert text_to_number("ONE") == 1
        assert text_to_number("Two") == 2
        assert text_to_number("ZERO") == 0
    
    def test_with_punctuation(self):
        """Test text with punctuation is cleaned."""
        assert text_to_number("one!") == 1
        assert text_to_number("two.") == 2
        assert text_to_number("three?") == 3
    
    def test_invalid_text(self):
        """Test invalid text raises ValueError."""
        with pytest.raises(ValueError, match="Unable to convert text to number"):
            text_to_number("invalid")
        with pytest.raises(ValueError, match="Unable to convert text to number"):
            text_to_number("not a number")
    
    def test_compound_numbers(self):
        """Test compound number conversion."""
        assert text_to_number("eleven") == 11
        assert text_to_number("forty two") == 42
        assert text_to_number("one hundred") == 100


class TestNumberToText:
    """Test number to text conversion functionality."""
    
    def test_small_numbers(self):
        """Test conversion of small numbers."""
        assert number_to_text(0) == "zero"
        assert number_to_text(1) == "one"
        assert number_to_text(5) == "five"
        assert number_to_text(10) == "ten"
        assert number_to_text(15) == "fifteen"
        assert number_to_text(42) == "forty-two"
    
    def test_large_numbers(self):
        """Test conversion of larger numbers."""
        assert number_to_text(100) == "one hundred"
        assert number_to_text(1000) == "one thousand"
        assert number_to_text(1234) == "one thousand, two hundred and thirty-four"
    
    def test_negative_numbers(self):
        """Test conversion of negative numbers."""
        assert number_to_text(-1) == "minus one"
        assert number_to_text(-42) == "minus forty-two"
    
    def test_zero(self):
        """Test zero conversion."""
        assert number_to_text(0) == "zero"


class TestBase64Conversions:
    """Test base64 conversion functionality with little-endian byte order."""
    
    def test_small_numbers(self):
        """Test base64 conversion of small numbers."""
        # Test 0
        assert number_to_base64(0) == base64.b64encode(b'\x00').decode('utf-8')
        assert base64_to_number(number_to_base64(0)) == 0
        
        # Test 1
        assert number_to_base64(1) == base64.b64encode((1).to_bytes(1, 'little', signed=True)).decode('utf-8')
        assert base64_to_number(number_to_base64(1)) == 1
        
        # Test 255 (requires 2 bytes with signed=True)
        assert number_to_base64(255) == base64.b64encode((255).to_bytes(2, 'little', signed=True)).decode('utf-8')
        assert base64_to_number(number_to_base64(255)) == 255
    
    def test_medium_numbers(self):
        """Test base64 conversion of medium numbers."""
        # Test 256 (requires two bytes with signed=True)
        assert number_to_base64(256) == base64.b64encode((256).to_bytes(2, 'little', signed=True)).decode('utf-8')
        assert base64_to_number(number_to_base64(256)) == 256
        
        # Test 65535 (requires 3 bytes with signed=True)
        assert number_to_base64(65535) == base64.b64encode((65535).to_bytes(3, 'little', signed=True)).decode('utf-8')
        assert base64_to_number(number_to_base64(65535)) == 65535
    
    def test_large_numbers(self):
        """Test base64 conversion of large numbers."""
        # Test 65536 (requires 3 bytes with signed=True)
        assert number_to_base64(65536) == base64.b64encode((65536).to_bytes(3, 'little', signed=True)).decode('utf-8')
        assert base64_to_number(number_to_base64(65536)) == 65536
        
        # Test 1000000
        assert base64_to_number(number_to_base64(1000000)) == 1000000
    
    def test_negative_numbers(self):
        """Test base64 conversion of negative numbers."""
        # Test -1
        assert base64_to_number(number_to_base64(-1)) == -1
        
        # Test -42
        assert base64_to_number(number_to_base64(-42)) == -42
    
    def test_invalid_base64(self):
        """Test invalid base64 input."""
        with pytest.raises(ValueError, match="Invalid base64 input"):
            base64_to_number("invalid_base64!")
        
        with pytest.raises(ValueError, match="Invalid base64 input"):
            base64_to_number("")
        
        with pytest.raises(ValueError, match="Invalid base64 input"):
            base64_to_number("not_base64")
        
        with pytest.raises(ValueError, match="Invalid base64 input"):
            base64_to_number("123!@#")


class TestFlaskApp:
    """Test Flask application endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_index_route(self, client):
        """Test index route returns HTML."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'html' in response.data.lower()
    
    def test_convert_text_to_decimal(self, client):
        """Test converting text to decimal."""
        response = client.post('/convert', 
                              json={'input': 'five', 'inputType': 'text', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] == '5'
        assert data['error'] is None
    
    def test_convert_decimal_to_text(self, client):
        """Test converting decimal to text."""
        response = client.post('/convert', 
                              json={'input': '5', 'inputType': 'decimal', 'outputType': 'text'})
        data = json.loads(response.data)
        assert data['result'] == 'five'
        assert data['error'] is None
    
    def test_convert_binary_to_hexadecimal(self, client):
        """Test converting binary to hexadecimal."""
        response = client.post('/convert', 
                              json={'input': '1010', 'inputType': 'binary', 'outputType': 'hexadecimal'})
        data = json.loads(response.data)
        assert data['result'] == 'a'
        assert data['error'] is None
    
    def test_convert_hexadecimal_to_octal(self, client):
        """Test converting hexadecimal to octal."""
        response = client.post('/convert', 
                              json={'input': 'ff', 'inputType': 'hexadecimal', 'outputType': 'octal'})
        data = json.loads(response.data)
        assert data['result'] == '377'
        assert data['error'] is None
    
    def test_convert_decimal_to_base64(self, client):
        """Test converting decimal to base64."""
        response = client.post('/convert', 
                              json={'input': '255', 'inputType': 'decimal', 'outputType': 'base64'})
        data = json.loads(response.data)
        # 255 in little-endian with signed=True (requires 2 bytes)
        expected = base64.b64encode((255).to_bytes(2, 'little', signed=True)).decode('utf-8')
        assert data['result'] == expected
        assert data['error'] is None
    
    def test_convert_base64_to_decimal(self, client):
        """Test converting base64 to decimal."""
        # 255 in little-endian with signed=True (requires 2 bytes)
        b64_value = base64.b64encode((255).to_bytes(2, 'little', signed=True)).decode('utf-8')
        response = client.post('/convert', 
                              json={'input': b64_value, 'inputType': 'base64', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] == '255'
        assert data['error'] is None
    
    def test_convert_text_to_binary(self, client):
        """Test converting text to binary."""
        response = client.post('/convert', 
                              json={'input': 'ten', 'inputType': 'text', 'outputType': 'binary'})
        data = json.loads(response.data)
        assert data['result'] == '1010'
        assert data['error'] is None
    
    def test_convert_octal_to_text(self, client):
        """Test converting octal to text."""
        response = client.post('/convert', 
                              json={'input': '12', 'inputType': 'octal', 'outputType': 'text'})
        data = json.loads(response.data)
        assert data['result'] == 'ten'
        assert data['error'] is None
    
    def test_convert_hexadecimal_to_text(self, client):
        """Test converting hexadecimal to text."""
        response = client.post('/convert', 
                              json={'input': 'a', 'inputType': 'hexadecimal', 'outputType': 'text'})
        data = json.loads(response.data)
        assert data['result'] == 'ten'
        assert data['error'] is None
    
    def test_convert_binary_to_octal(self, client):
        """Test converting binary to octal."""
        response = client.post('/convert', 
                              json={'input': '1010', 'inputType': 'binary', 'outputType': 'octal'})
        data = json.loads(response.data)
        assert data['result'] == '12'
        assert data['error'] is None
    
    def test_convert_octal_to_hexadecimal(self, client):
        """Test converting octal to hexadecimal."""
        response = client.post('/convert', 
                              json={'input': '12', 'inputType': 'octal', 'outputType': 'hexadecimal'})
        data = json.loads(response.data)
        assert data['result'] == 'a'
        assert data['error'] is None
    
    def test_convert_decimal_to_binary(self, client):
        """Test converting decimal to binary."""
        response = client.post('/convert', 
                              json={'input': '10', 'inputType': 'decimal', 'outputType': 'binary'})
        data = json.loads(response.data)
        assert data['result'] == '1010'
        assert data['error'] is None
    
    def test_convert_binary_to_decimal(self, client):
        """Test converting binary to decimal."""
        response = client.post('/convert', 
                              json={'input': '1010', 'inputType': 'binary', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] == '10'
        assert data['error'] is None
    
    def test_convert_hexadecimal_to_decimal(self, client):
        """Test converting hexadecimal to decimal."""
        response = client.post('/convert', 
                              json={'input': 'a', 'inputType': 'hexadecimal', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] == '10'
        assert data['error'] is None
    
    def test_convert_octal_to_decimal(self, client):
        """Test converting octal to decimal."""
        response = client.post('/convert', 
                              json={'input': '12', 'inputType': 'octal', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] == '10'
        assert data['error'] is None
    
    def test_convert_decimal_to_octal(self, client):
        """Test converting decimal to octal."""
        response = client.post('/convert', 
                              json={'input': '10', 'inputType': 'decimal', 'outputType': 'octal'})
        data = json.loads(response.data)
        assert data['result'] == '12'
        assert data['error'] is None
    
    def test_convert_decimal_to_hexadecimal(self, client):
        """Test converting decimal to hexadecimal."""
        response = client.post('/convert', 
                              json={'input': '10', 'inputType': 'decimal', 'outputType': 'hexadecimal'})
        data = json.loads(response.data)
        assert data['result'] == 'a'
        assert data['error'] is None
    
    def test_convert_text_to_octal(self, client):
        """Test converting text to octal."""
        response = client.post('/convert', 
                              json={'input': 'ten', 'inputType': 'text', 'outputType': 'octal'})
        data = json.loads(response.data)
        assert data['result'] == '12'
        assert data['error'] is None
    
    def test_convert_text_to_hexadecimal(self, client):
        """Test converting text to hexadecimal."""
        response = client.post('/convert', 
                              json={'input': 'ten', 'inputType': 'text', 'outputType': 'hexadecimal'})
        data = json.loads(response.data)
        assert data['result'] == 'a'
        assert data['error'] is None
    
    def test_convert_text_to_binary(self, client):
        """Test converting text to binary."""
        response = client.post('/convert', 
                              json={'input': 'ten', 'inputType': 'text', 'outputType': 'binary'})
        data = json.loads(response.data)
        assert data['result'] == '1010'
        assert data['error'] is None
    
    def test_convert_text_to_base64(self, client):
        """Test converting text to base64."""
        response = client.post('/convert', 
                              json={'input': 'ten', 'inputType': 'text', 'outputType': 'base64'})
        data = json.loads(response.data)
        # 10 in little-endian with signed=True (requires 1 byte)
        expected = base64.b64encode((10).to_bytes(1, 'little', signed=True)).decode('utf-8')
        assert data['result'] == expected
        assert data['error'] is None
    
    def test_convert_binary_to_base64(self, client):
        """Test converting binary to base64."""
        response = client.post('/convert', 
                              json={'input': '1010', 'inputType': 'binary', 'outputType': 'base64'})
        data = json.loads(response.data)
        # 10 in little-endian with signed=True (requires 1 byte)
        expected = base64.b64encode((10).to_bytes(1, 'little', signed=True)).decode('utf-8')
        assert data['result'] == expected
        assert data['error'] is None
    
    def test_convert_octal_to_base64(self, client):
        """Test converting octal to base64."""
        response = client.post('/convert', 
                              json={'input': '12', 'inputType': 'octal', 'outputType': 'base64'})
        data = json.loads(response.data)
        # 10 in little-endian with signed=True (requires 1 byte)
        expected = base64.b64encode((10).to_bytes(1, 'little', signed=True)).decode('utf-8')
        assert data['result'] == expected
        assert data['error'] is None
    
    def test_convert_hexadecimal_to_base64(self, client):
        """Test converting hexadecimal to base64."""
        response = client.post('/convert', 
                              json={'input': 'a', 'inputType': 'hexadecimal', 'outputType': 'base64'})
        data = json.loads(response.data)
        # 10 in little-endian with signed=True (requires 1 byte)
        expected = base64.b64encode((10).to_bytes(1, 'little', signed=True)).decode('utf-8')
        assert data['result'] == expected
        assert data['error'] is None
    
    def test_convert_base64_to_text(self, client):
        """Test converting base64 to text."""
        # 10 in little-endian with signed=True (requires 1 byte)
        b64_value = base64.b64encode((10).to_bytes(1, 'little', signed=True)).decode('utf-8')
        response = client.post('/convert', 
                              json={'input': b64_value, 'inputType': 'base64', 'outputType': 'text'})
        data = json.loads(response.data)
        assert data['result'] == 'ten'
        assert data['error'] is None
    
    def test_convert_base64_to_binary(self, client):
        """Test converting base64 to binary."""
        # 10 in little-endian with signed=True (requires 1 byte)
        b64_value = base64.b64encode((10).to_bytes(1, 'little', signed=True)).decode('utf-8')
        response = client.post('/convert', 
                              json={'input': b64_value, 'inputType': 'base64', 'outputType': 'binary'})
        data = json.loads(response.data)
        assert data['result'] == '1010'
        assert data['error'] is None
    
    def test_convert_base64_to_octal(self, client):
        """Test converting base64 to octal."""
        # 10 in little-endian with signed=True (requires 1 byte)
        b64_value = base64.b64encode((10).to_bytes(1, 'little', signed=True)).decode('utf-8')
        response = client.post('/convert', 
                              json={'input': b64_value, 'inputType': 'base64', 'outputType': 'octal'})
        data = json.loads(response.data)
        assert data['result'] == '12'
        assert data['error'] is None
    
    def test_convert_base64_to_hexadecimal(self, client):
        """Test converting base64 to hexadecimal."""
        # 10 in little-endian with signed=True (requires 1 byte)
        b64_value = base64.b64encode((10).to_bytes(1, 'little', signed=True)).decode('utf-8')
        response = client.post('/convert', 
                              json={'input': b64_value, 'inputType': 'base64', 'outputType': 'hexadecimal'})
        data = json.loads(response.data)
        assert data['result'] == 'a'
        assert data['error'] is None


class TestErrorHandling:
    """Test error handling for various edge cases."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_invalid_input_type(self, client):
        """Test invalid input type."""
        response = client.post('/convert', 
                              json={'input': '10', 'inputType': 'invalid', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'Invalid input type' in data['error']
    
    def test_invalid_output_type(self, client):
        """Test invalid output type."""
        response = client.post('/convert', 
                              json={'input': '10', 'inputType': 'decimal', 'outputType': 'invalid'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'Invalid output type' in data['error']
    
    def test_invalid_binary_input(self, client):
        """Test invalid binary input."""
        response = client.post('/convert', 
                              json={'input': '102', 'inputType': 'binary', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'error' in data
    
    def test_invalid_octal_input(self, client):
        """Test invalid octal input."""
        response = client.post('/convert', 
                              json={'input': '89', 'inputType': 'octal', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'error' in data
    
    def test_invalid_hexadecimal_input(self, client):
        """Test invalid hexadecimal input."""
        response = client.post('/convert', 
                              json={'input': 'gh', 'inputType': 'hexadecimal', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'error' in data
    
    def test_invalid_base64_input(self, client):
        """Test invalid base64 input."""
        response = client.post('/convert', 
                              json={'input': 'invalid!', 'inputType': 'base64', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'Invalid base64 input' in data['error']
    
    def test_invalid_text_input(self, client):
        """Test invalid text input."""
        response = client.post('/convert', 
                              json={'input': 'invalid', 'inputType': 'text', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'Unable to convert text to number' in data['error']
    
    def test_compound_text_input(self, client):
        """Test compound text input that should work."""
        response = client.post('/convert', 
                              json={'input': 'eleven', 'inputType': 'text', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] == '11'
        assert data['error'] is None
    
    def test_readme_examples(self, client):
        """Test examples from README.md should work."""
        # Example 1: Convert decimal to binary: Input "42" with input type "decimal" and output type "binary"
        response = client.post('/convert', 
                              json={'input': '42', 'inputType': 'decimal', 'outputType': 'binary'})
        data = json.loads(response.data)
        assert data['result'] == '101010'
        assert data['error'] is None
        
        # Example 2: Convert text to decimal: Input "forty two" with input type "text" and output type "decimal"
        response = client.post('/convert', 
                              json={'input': 'forty two', 'inputType': 'text', 'outputType': 'decimal'})
        data = json.loads(response.data)
        # This should work but currently fails due to bug in text_to_number function
        assert data['result'] == '42'  # This will fail with current implementation
        assert data['error'] is None
        
        # Example 3: Convert hexadecimal to text: Input "2a" with input type "hexadecimal" and output type "text"
        response = client.post('/convert', 
                              json={'input': '2a', 'inputType': 'hexadecimal', 'outputType': 'text'})
        data = json.loads(response.data)
        assert data['result'] == 'forty-two'
        assert data['error'] is None
    
    def test_missing_json_data(self, client):
        """Test missing JSON data."""
        response = client.post('/convert', data='invalid json')
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'error' in data
    
    def test_missing_input_field(self, client):
        """Test missing input field."""
        response = client.post('/convert', 
                              json={'inputType': 'decimal', 'outputType': 'binary'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'error' in data
    
    def test_missing_input_type_field(self, client):
        """Test missing inputType field."""
        response = client.post('/convert', 
                              json={'input': '10', 'outputType': 'binary'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'error' in data
    
    def test_missing_output_type_field(self, client):
        """Test missing outputType field."""
        response = client.post('/convert', 
                              json={'input': '10', 'inputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'error' in data


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_zero_conversions(self, client):
        """Test zero in all formats."""
        # Zero in all input formats
        for input_type in ['decimal', 'binary', 'octal', 'hexadecimal']:
            response = client.post('/convert', 
                                  json={'input': '0', 'inputType': input_type, 'outputType': 'decimal'})
            data = json.loads(response.data)
            assert data['result'] == '0'
            assert data['error'] is None
        
        # Zero text
        response = client.post('/convert', 
                              json={'input': 'zero', 'inputType': 'text', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] == '0'
        assert data['error'] is None
    
    def test_large_numbers(self, client):
        """Test large numbers."""
        large_number = '1000000'
        response = client.post('/convert', 
                              json={'input': large_number, 'inputType': 'decimal', 'outputType': 'binary'})
        data = json.loads(response.data)
        assert data['result'] == bin(int(large_number))[2:]
        assert data['error'] is None
    
    def test_negative_numbers(self, client):
        """Test negative numbers."""
        response = client.post('/convert', 
                              json={'input': '-10', 'inputType': 'decimal', 'outputType': 'text'})
        data = json.loads(response.data)
        assert data['result'] == 'minus ten'
        assert data['error'] is None
    
    def test_negative_binary_conversion(self, client):
        """Test negative number to binary conversion."""
        response = client.post('/convert', 
                              json={'input': '-5', 'inputType': 'decimal', 'outputType': 'binary'})
        data = json.loads(response.data)
        # Should return proper binary representation (101, not b101)
        assert data['result'] == '101'
        assert data['error'] is None
    
    def test_negative_octal_conversion(self, client):
        """Test negative number to octal conversion."""
        response = client.post('/convert', 
                              json={'input': '-5', 'inputType': 'decimal', 'outputType': 'octal'})
        data = json.loads(response.data)
        # Should return proper octal representation (5, not o5)
        assert data['result'] == '5'
        assert data['error'] is None
    
    def test_negative_hex_conversion(self, client):
        """Test negative number to hexadecimal conversion."""
        response = client.post('/convert', 
                              json={'input': '-5', 'inputType': 'decimal', 'outputType': 'hexadecimal'})
        data = json.loads(response.data)
        # Should return proper hex representation (5, not x5)
        assert data['result'] == '5'
        assert data['error'] is None
    
    def test_empty_input(self, client):
        """Test empty input."""
        response = client.post('/convert', 
                              json={'input': '', 'inputType': 'decimal', 'outputType': 'binary'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'error' in data
    
    def test_whitespace_input(self, client):
        """Test input with whitespace."""
        response = client.post('/convert', 
                              json={'input': '  10  ', 'inputType': 'decimal', 'outputType': 'binary'})
        data = json.loads(response.data)
        assert data['result'] == '1010'
        assert data['error'] is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
