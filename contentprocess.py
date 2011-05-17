def int_from_4bytes(b3, b2, b1, b0):
    return (((((b3 << 8) + b2) << 8) + b1) << 8) + b0

def int_to_4bytes(n):
    r = []
    n &= 0xFFFFFFFFL
    for i in range(4):
        r.append(n & 0xFF)
        n >>= 8
    r.reverse()
    return tuple(r)

def int_from_3bytes(b2, b1, b0):
    return (((b2 << 8) + b1) << 8) + b0

def int_to_3bytes(n):
    r = []
    n &= 0xFFFFFF
    for i in range(3):
        r.append(n & 0xFF)
        n >>= 8
    r.reverse()
    return tuple(r)

def int_from_2bytes(b1, b0):
    return (b1 << 8) + b0

def int_to_2bytes(n):
    r = []
    n &= 0xFFFF
    for i in range(2):
        r.append(n & 0xFF)
        n >>= 8
    r.reverse()
    return tuple(r)

def lintoascii(n):
    a=''
    for x in int_to_2bytes(n):
    	a=a+chr(x)
    return a

def asciitolin(s):
    return int_from_2bytes(ord(s[0]),ord(s[1]))

def inttoascii(n):
    a=''
    for x in int_to_4bytes(n):
        a=a+chr(x)
    return a

def asciitoint(s):
    return int_from_4bytes(ord(s[0]),ord(s[1]),ord(s[2]),ord(s[3]))

