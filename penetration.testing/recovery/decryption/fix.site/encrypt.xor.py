if __name__ == '__main__':
    import sys
    import os

    # Usage: python encrypt.py ./backup.txt ./htdocs/
    key_f = sys.argv[1]
    key_fp = open(key_f, 'r')
    key = key_fp.readline().strip()
    key_fp.close()

    enc_dir = sys.argv[2]
    for file in os.listdir(enc_dir):
        fpath = os.path.join(enc_dir, file)
        data = open(fpath, 'rb')
        result = ""
        i = 0
        while 1:
            byte_s = data.read(1)
            if not byte_s:
                break
            result += chr(ord(byte_s) ^ ord(key[i]))
            i = (i + 1) % len(key)
        data.close()
        out_f = open(fpath, 'w')
        out_f.write(result)
        out_f.close()
