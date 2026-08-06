python3 -c 'e=open("encrypted.bin","rb").read(); p=b"THM{"; k=bytes(e[i]^p[i] for i in range(4)); print(bytes(x^k[i%4] for i,x in enumerate(e)).decode())'
