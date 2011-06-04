def decrypt(stream):
    def gen():
        for i, c in enumerate(stream):
            c = ord(c)
            lo_bits = i & 0x03
            if lo_bits == 0:
                yield c ^ 0x49
            elif lo_bits == 1:
                yield c ^ 0x43
            elif lo_bits == 2:
                yield c ^ 0x46
            elif lo_bits == 3:
                yield c ^ 0x50
    return ''.join(chr(c) for c in gen())

if __name__ == '__main__':
    print 'yo?'
    with open('unpacked/0', 'rb') as input:
        with open('0.decrypted.png', 'wb') as output:
            output.write(decrypt(input.read()))
    with open('unpacked/1', 'rb') as input:
        with open('1.decrypted.png', 'wb') as output:
            output.write(decrypt(input.read()))
    print 'yay'
