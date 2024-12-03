import os
import time
import hashlib
import requests
from tqdm import tqdm


TMP_DIR = os.environ.get("WEB_KIT_TMP_DIR") or "/tmp"


def touch(path):
    with open(path, "a"):
        os.utime(path, None)


def try_remove(path):
    try:
        os.remove(path)
    except Exception:
        pass


def download_url_asset(url: str,
                       tmp_dir: str = TMP_DIR,
                       lock_timeout_seconds=300) -> str:
    """
    load asset and return local path.
    raise Exception if asset absent.

    """

    slug_name = hashlib.md5(url.encode()).hexdigest()
    local_path = os.path.join(TMP_DIR, f"asset__{slug_name}")
    lock_path = f"{local_path}.lock"

    def wait_for_lock():
        while os.path.exists(lock_path):
            try:
                lock_ctime = os.path.getctime(lock_path)
                lock_elapsed = time.time() - lock_ctime
                if lock_elapsed > lock_timeout_seconds:
                    print(f"remove lock: {lock_path}")
                    try_remove(lock_path)
                    break
            except Exception:
                pass
            print(f"wait for lock: {lock_path}")
            time.sleep(5)

    def download_file():
        print(f"downloading {url} to {local_path}")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Ensure we got a successful response

            total_size_in_bytes = int(response.headers.get('content-length', 0))
            # 1 Kibibyte
            block_size = 1024
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(block_size):
                    progress_bar.update(len(chunk))
                    f.write(chunk)
            progress_bar.close()

            if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                print("ERROR, something went wrong")

        except Exception as e:
            try_remove(local_path)
            raise e
        finally:
            try_remove(lock_path)

    while True:
        wait_for_lock()

        if os.path.exists(local_path):
            print("local asset found.")
            local_asset_size = os.path.getsize(local_path)
            print(f"local asset size: {local_asset_size}")
            remote_asset_size = int(requests.head(url).headers.get('content-length', 0))
            print(f"remote asset size: {remote_asset_size}")
            if local_asset_size == remote_asset_size:
                print("local asset size matches remote asset size.")
                return local_path

        if os.path.exists(lock_path):
            continue

        touch(lock_path)
        download_file()
        return local_path

    