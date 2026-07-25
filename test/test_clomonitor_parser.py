import unittest
import socket
from unittest.mock import patch, MagicMock

# Import the functions from your refactored script
# Make sure your main script is saved as clomonitor_parser.py
from lfx_tac_actions.updateclomonitor import (
    is_safe_url,
    load_from_artwork_repo,
    parse_repositories
)

class TestClomonitorParser(unittest.TestCase):

    # --- Tests for SSRF Protection (is_safe_url) ---

    @patch('socket.gethostbyname')
    def test_is_safe_url_valid(self, mock_dns):
        """Test that a standard, external HTTP/HTTPS URL is permitted."""
        # Mock DNS to return a safe, public IP
        mock_dns.return_value = '8.8.8.8'

        self.assertTrue(is_safe_url('https://example.com/api/data'))
        self.assertTrue(is_safe_url('http://example.com'))

    def test_is_safe_url_invalid_scheme(self):
        """Test that non-HTTP(s) schemes are rejected."""
        self.assertFalse(is_safe_url('ftp://example.com'))
        self.assertFalse(is_safe_url('file:///etc/passwd'))
        self.assertFalse(is_safe_url('gopher://example.com'))

    @patch('socket.gethostbyname')
    def test_is_safe_url_ssrf_private_ip(self, mock_dns):
        """Test that URLs resolving to private or loopback IPs are blocked."""
        # Test Loopback
        mock_dns.return_value = '127.0.0.1'
        self.assertFalse(is_safe_url('http://localhost'))

        # Test Private Network (e.g., 10.x.x.x, 192.168.x.x)
        mock_dns.return_value = '192.168.1.5'
        self.assertFalse(is_safe_url('http://internal-server.local'))

    @patch('socket.gethostbyname')
    def test_is_safe_url_unresolvable(self, mock_dns):
        """Test that a hostname that fails to resolve is rejected."""
        mock_dns.side_effect = socket.gaierror("Name or service not known")
        self.assertFalse(is_safe_url('https://this-does-not-exist.local'))


    # --- Tests for Repository Parsing ---

    def test_parse_repositories(self):
        """Test that repositories are parsed correctly and exclude lists are added."""
        raw_repos = [
            {'url': 'https://github.com/myorg/my-awesome-repo'},
            {'url': 'https://github.com/myorg/another-repo'}
        ]
        parsed = parse_repositories(raw_repos)

        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]['name'], 'my-awesome-repo')
        self.assertEqual(parsed[0]['url'], 'https://github.com/myorg/my-awesome-repo')
        self.assertEqual(parsed[0]['exclude'], ['clomonitor'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
