import urllib
import sys
import time
import os
import zipfile

out_dir = '/media/DataDisk/TCIA_LGG_TEST/'

if not os.path.exists(out_dir):
    os.makedirs(out_dir)


def reporthook(count, block_size, total_size):
    # Obtained from: https://blog.shichao.io/2012/10/04/progress_speed_indicator_for_urlretrieve_in_python.html
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write("\r...%d%%, %d MB, %d KB/s, %d seconds passed" %
                    (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()


out_file = os.path.join(out_dir, 'Segmentations.zip')
urlReader = urllib.URLopener()

# Download URL changes everytime, need to get API key
download_URL="N/A"

urlReader.retrieve(download_URL, out_file, reporthook)

zip_ref = zipfile.ZipFile(out_file, 'r')
zip_ref.extractall(out_dir)
zip_ref.close()
