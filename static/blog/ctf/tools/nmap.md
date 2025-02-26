# NMap - Network Mapper

A host scanning tool. Very popular and well known among hackers and IT professionals alike.

## Quick start
To run a full, in-depth scan of the host, use the flags `-sC` and `-sV` to run some common
sense scripts and detect the operating system version.

    #!sh
    nmap -sC -sV $target_ip

To do a "stealth" scan of the host, use the `-sS` flag. (requires admin privileges)

    #!sh
    nmap -sS $target_ip

<small>_NOTE_: this can, in some situations, not be as "stealthy" if the target machine is expecting this type of scan to occur.</small>

## Other useful options
`-v` is the shorthand for verbosity. its controlled with increasing the `v` count on this flag. For example verbosity level `3` is `-vvv`