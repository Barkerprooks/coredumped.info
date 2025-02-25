Network Map

A host port scanning tool. very popular and well known among hackers and IT professionals alike.

##### Quick start
Doing an in-depth scan of a host
```
nmap -sC -sV $target_ip
```

Doing a "stealth" scan of the host (requires `root`)
```
sudo nmap -sS $target_ip
```

_NOTE_: this can, in some situations, not be as "stealthy" if the target machine is expecting this type of scan to occur.

##### Other useful options
`-v` is the shorthand for verbosity. its controlled with increasing the v count on this flag. For example verbosity level 3 is `-vvv`