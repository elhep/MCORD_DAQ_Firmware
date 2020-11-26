# Booting AFCK with ARTIQ

1. Load GW with bootloader 

```
artiq_flash --srcbuild -d ./mcord -V single_tdc -t afck1v1 load
```

Where `./mcord` is a directory with prebuilt firmware, and `single_tdc` is a subdirectory within `./mcord` with specific firmware variant to be used.

3. Check if device responds to ping, as it happens not to respond. Then try to hard-restart chassis.

```
ping 192.168.95.2020
```

4. If device reposnds to ping, netboot ARTIQ firmware:

```
artiq_netboot -b -f ./mcord/single_tdc/software/runtime/runtime.bin 192.168.95.202
```
