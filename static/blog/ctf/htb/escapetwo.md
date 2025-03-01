# EscapeTwo
In progress...

- `10.10.11.51`
- Windows
- Easy

Windows machines are not my strong suit, so I need to get more practice in this regard. 
Fortunetely this is a pretty highly rated easy machine, so let's get started.

Interesting for this one. I don't usually see this on HTB. But we are given credentials right away. 

- username: `rose`
- password: `KxEPkKe6R8su`


When scanning Windows machines we need the `-Pn` flag due to Windows not responding to ping from nmap. 

    nmap -Pn -sC -sV -vv 10.10.11.51

Wow it looks like there's a lot going on. Its possibly a domain controller.

Here's the first few ports before `NSE` starts doing its thing. 

Notably we have a `DNS` server. Also the usual `SMB` ports are open.

    PORT     STATE SERVICE       REASON  VERSION
    53/tcp   open  domain        syn-ack Simple DNS Plus
    88/tcp   open  kerberos-sec  syn-ack Microsoft Windows Kerberos (server time: 2025-02-26 22:08:04Z)
    135/tcp  open  msrpc         syn-ack Microsoft Windows RPC
    139/tcp  open  netbios-ssn   syn-ack Microsoft Windows netbios-ssn
    389/tcp  open  ldap          syn-ack Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)

`LDAP` seems to be showing us some domain names. We can go ahead and add those to `/etc/hosts`. 

    |_ssl-date: 2025-02-26T22:08:51+00:00; -1s from scanner time.
    | ssl-cert: Subject: commonName=DC01.sequel.htb
    | Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC01.sequel.htb
    | Issuer: commonName=sequel-DC01-CA/domainComponent=sequel
    | Public Key type: rsa
    | Public Key bits: 2048

It looks like encryption is standard too. 

Here's the next few ports

    445/tcp  open  microsoft-ds? syn-ack
    464/tcp  open  kpasswd5?     syn-ack
    593/tcp  open  ncacn_http    syn-ack Microsoft Windows RPC over HTTP 1.0
    636/tcp  open  ssl/ldap      syn-ack Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)

This could be interesting... An exposed MSSQL server? 

    1433/tcp open  ms-sql-s      syn-ack Microsoft SQL Server 2019 15.00.2000.00; RTM
    | ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback

So... given that we started with creds. Lets just try enumerating the `SMB` shares first?

    smbclient -U rose -L //DC01.sequel.htb/
    Password for [WORKGROUP\rose]: <enter password>

Cool. Here are the available shares.

    Sharename       Type      Comment
    ---------       ----      -------
    Accounting Department Disk
    ADMIN$          Disk      Remote Admin
    C$              Disk      Default share
    IPC$            IPC       Remote IPC
    NETLOGON        Disk      Logon server share
    SYSVOL          Disk      Logon server share
    Users           Disk

Logging into users, we have a pretty standard user folder layout for Windows machines.
You can recursively grab the files with `smbclient` using this
snippit. 

    mask ""
    recurse on
    prompt off
    mget *

If we download all the files and look through them, there doesn't seem to by any red flags or obvious files. It looks like a fresh install. 

Lets look at `SYSVOL`. 

    smbclient -U rose //DC01.sequel.htb/sysvol
    Password for [WORKGROUP\rose]: <enter password> 

We are greeted with one folder called `sequel.htb`. There are three more folders inside it.  

    smb: \sequel.htb\> dir
    .                                   D        0  Sat Jun  8 11:46:03 2024
    ..                                  D        0  Sat Jun  8 11:46:03 2024
    DfsrPrivate                      DHSr        0  Sat Jun  8 11:46:03 2024
    Policies                            D        0  Sat Jun  8 11:39:50 2024
    scripts                             D        0  Sat Jun  8 11:39:46 2024

                6367231 blocks of size 4096. 920683 blocks available

