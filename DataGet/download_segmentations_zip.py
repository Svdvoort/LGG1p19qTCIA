import urllib
import sys
import time
import os

out_dir = '/media/DataDisk/TCIA_LGG/'

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

download_URL="https://public.boxcloud.com/d/1/yiL5lxJFvCkkGwrmxSWkB2Q-DVKVB0QE4IXvMO3r7XrXCWG8VAxsH1iTttQbYrsrxsmJu6v1slNC6FSTrKVG412HMWK4Kc7gIDrA5NAEaN3esv_nd3rm6-5ssyFadgxMSKk7_1SyWBMvV0WYZ3ilHu6EwxohaHptUun1WDNOUQ6-TO3QYClVMEpN1By2vv1SXpeSgyxWBoTv2bWY7Qy5OnZ1-54Ie8b-4msGXqCHc6dglkYxG-mon6waJ78g8ia7R4CnOn5FHzyUvntZy6j5GL07GXEznb_r5NwVq-Wo7-axMiONQmb2G2WG4fEAhjbqucAolBM1nwzga5Tt2CwkU4nViIa6nkJNcZLGtXrikTAmtIOOENOL7JSBTmGZB2CzVa0EEUGBi7pGzHqCGDZCd32EriXa_ZUwIm1rmm_dQgqMiv190lF41WWuElHBRTy1Y_1kiAgyz7qUt14JzRkkAhrPXDSKAAh6SMpKYVWWXW24DGhad6On2fjJrnkdJZYQvSzmlTyhD6-FUG7oC6Y5QxBu8_UBuNEQgoBkmqAZT9U7Mmsx7wrLuLLryZ5chaCaszX2-k31u5iy0kwwxK6jnA5zfW6AlnxIQmR2BthqCS24ULX0NVpCEAqRxzxzl6dsj1e86r6IJhTpXOHg5LKUnfw7MFv1v6oDUHfNEiZtzL99qto-rS_ssm-r7gVtiaAJ5qLJit9Tu7lSoOhfFI_1Bb0qxsgs7dFm7urKxShWHWQ_7OvGkEnFDw_RtsvpAERcsU4dhkJpTX4fDDrnRKtytTDte0nD92pQuthMu5D6HBvUZnG92P5h6NzSYTgfikB8XQNwt3xmLTb2o_-lScriHhV0nVZYgROiUjVFTOCxGzPFacMKm2kz4f_UZ0coVp97NVm3bzK59HkT4Onqccg_Lxt8i_wcxw7CBG5HCR8Wo4VEqY69DwJ_9Fv3r5rpxp4EfTnexvRCN3H7I3gJV7kjTOSuaqyh2iLOFzNsDd1_l31p4cPLuAR6sk8BSD7VvcBE-54e9IGYPk1Kko-O5x2kcX7icS0yStHu-Idz1gahIaZnPVq_lfF7dTevAaZRmrQwkCjCWjEWwoY5iCTlKDkyp-_ZU8owRSfrVOimIgUoxIx0WkHwBuxGCvL1POL_M48ZhXjdsfv-xT8FUYyX6OPzpU9bVXWKIA4SSXG9G8C0whgN4lkWTqWh_2CtPql3XU_DcBDq9Z83WTsoGL41u5Ngfq6OjAQ./download"

urlReader.retrieve(download_URL, out_file, reporthook)
