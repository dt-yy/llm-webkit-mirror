import os
import time
import hashlib
from unittest.mock import patch, MagicMock
from llm_web_kit.libs.download_assets import (
    touch,
    try_remove,
    download_url_asset
)


class TestTouch:
    def setup_method(self):
        # Create a test file
        self.test_file = 'test_file'
        with open(self.test_file, 'w') as f:
            f.write('test')

    def teardown_method(self):
        # Remove the test file after each test
        os.remove(self.test_file)

    def test_touch_new_file(self):
        # Remove the test file
        os.remove(self.test_file)

        # Call the touch function
        touch(self.test_file)

        # Check that the file was created
        assert os.path.exists(self.test_file)

    def test_touch_existing_file(self):
        # Get the current access and modification times
        old_times = os.path.getatime(self.test_file), os.path.getmtime(self.test_file)

        # Wait for a second to ensure that the times will be updated
        time.sleep(1)

        # Call the touch function
        touch(self.test_file)

        # Get the new access and modification times
        new_times = os.path.getatime(self.test_file), os.path.getmtime(self.test_file)

        # Check that the times were updated
        assert old_times != new_times


class TestTryRemove:
    def setup_method(self):
        # Create a test file
        self.test_file = 'test_file'
        with open(self.test_file, 'w') as f:
            f.write('test')

    def teardown_method(self):
        # Remove the test file after each test
        try_remove(self.test_file)

    def test_try_remove_existing_file(self):
        # Call the try_remove function
        try_remove(self.test_file)

        # Check that the file was removed
        assert not os.path.exists(self.test_file)

    def test_try_remove_nonexistent_file(self):
        # Remove the test file
        os.remove(self.test_file)

        # Call the try_remove function
        try_remove(self.test_file)

        # Check that the file was not created
        assert not os.path.exists(self.test_file)


class TestDownloadUrlAsset:
    @patch('llm_web_kit.libs.download_assets.requests.head')
    @patch('llm_web_kit.libs.download_assets.requests.get')
    def test_download_url_asset(self, mock_get, mock_head):
        # Test case 1: First time download
        tmp_dir = '/tmp'
        dummy_content = b'test content'

        mock_head.return_value = MagicMock()
        mock_head.return_value.headers.get.return_value = len(dummy_content)

        mock_get.return_value = mock_response = MagicMock()
        mock_response.iter_content.return_value = [dummy_content]
        mock_response.headers.get.return_value = len(dummy_content)

        test_url = 'http://example.com/file1'
        target_path = f"{tmp_dir}/asset__{hashlib.md5(test_url.encode()).hexdigest()}"
        os.remove(target_path)
        res = download_url_asset(test_url, tmp_dir)
        assert res == target_path
        assert os.path.exists(res)
        with open(res, 'rb') as f:
            assert f.read() == dummy_content

        # Test case 2: File already exists
        mock_head.reset_mock()
        mock_get.reset_mock()
        res = download_url_asset(test_url, tmp_dir)
        assert os.path.exists(res)
        with open(res, 'rb') as f:
            assert f.read() == dummy_content
        mock_get.assert_not_called()

        # test modification
        with open(res, 'wb') as f:
            f.write(b'new content')

        mock_head.reset_mock()
        mock_get.reset_mock()
        res = download_url_asset(test_url, tmp_dir)
        assert os.path.exists(res)
        with open(res, 'rb') as f:
            assert f.read() == dummy_content
        mock_get.assert_called_once()
