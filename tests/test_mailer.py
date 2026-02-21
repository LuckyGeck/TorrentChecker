# -*- coding: utf-8 -*-

import pytest
from unittest.mock import MagicMock, patch, call
from email.mime.multipart import MIMEMultipart

from plugins.utils.mailer import build_table, send_email


class TestBuildTable:

    def test_returns_html_string(self):
        result = build_table('<tr><td>row</td></tr>')
        assert '<html>' in result
        assert '</html>' in result

    def test_embeds_contents(self):
        contents = '<tr><td>Episode S01E01</td></tr>'
        result = build_table(contents)
        assert contents in result

    def test_contains_table_tag(self):
        result = build_table('')
        assert '<table' in result
        assert '</table>' in result

    def test_empty_contents_still_valid_html(self):
        result = build_table('')
        assert '<html>' in result


class TestSendEmail:

    def _call(self, is_ssl=False, is_tls=False):
        send_email(
            smtp_host='smtp.example.com',
            is_ssl=is_ssl,
            is_tls=is_tls,
            login='user',
            password='pass',
            from_addr='from@example.com',
            to_addr='to@example.com',
            html_text='<html>body</html>',
            mail_text='plain body',
        )

    def test_uses_smtp_ssl_when_ssl_true(self):
        with patch('smtplib.SMTP_SSL') as mock_ssl, \
             patch('smtplib.SMTP'):
            mock_server = MagicMock()
            mock_ssl.return_value = mock_server
            self._call(is_ssl=True, is_tls=False)
            mock_ssl.assert_called_once_with('smtp.example.com', timeout=10)
            mock_server.login.assert_called_once_with('user', 'pass')
            mock_server.sendmail.assert_called_once()
            mock_server.quit.assert_called_once()

    def test_uses_smtp_when_ssl_false(self):
        with patch('smtplib.SMTP') as mock_smtp, \
             patch('smtplib.SMTP_SSL'):
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            self._call(is_ssl=False, is_tls=False)
            mock_smtp.assert_called_once_with('smtp.example.com', timeout=10)

    def test_starttls_called_when_tls_true(self):
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            self._call(is_ssl=False, is_tls=True)
            mock_server.starttls.assert_called_once()

    def test_starttls_not_called_when_tls_false(self):
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            self._call(is_ssl=False, is_tls=False)
            mock_server.starttls.assert_not_called()

    def test_sendmail_uses_correct_addresses(self):
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            self._call()
            args = mock_server.sendmail.call_args[0]
            assert args[0] == 'from@example.com'
            assert args[1] == 'to@example.com'
