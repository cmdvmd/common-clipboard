import win32clipboard as clipboard
import time


def get_copied_data():
    for fmt in formats:
        try:
            clipboard.OpenClipboard()
            return clipboard.GetClipboardData(fmt)
        except TypeError:
            continue
        finally:
            clipboard.CloseClipboard()
    else:
        raise TypeError('Unknown copied data')


def detect_changes():
    global current_data

    while True:
        new_data = get_copied_data()

        if new_data != current_data:
            current_data = new_data
            print(new_data)
        time.sleep(0.3)


formats = {clipboard.CF_UNICODETEXT: 'Text', clipboard.CF_DIB: 'Image'}

current_data = get_copied_data()

if __name__ == '__main__':
    try:
        detect_changes()
    except KeyboardInterrupt:
        pass
