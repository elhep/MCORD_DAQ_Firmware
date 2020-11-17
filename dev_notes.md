# 12 Oct

## Issue 1

Issue: It seems that AFCK sometimes fails to be available over network after loading gateware.

Narrow down concept: switch AFCK on and off and note if the board is pingable

Procedure:

Have ping active all the time

* Power on AFCK
* `artiq_flash -d ./ --srcbuild -V build -t afck1v1 load`
* Verify boot process

Sources: `FMC_ADC100M_10B_TDC_16cha_gw_20201012_NetworkBootTest.tgz`
DARTIQ: 0.1.2
DARTIQ-Image: 4f8b31c076a6

Results:

* RUN 0: Started from the first time
* RUN 1: Started from the first time
* RUN 2: Started from the first time
* RUN 3: No UART Boot message, retrying with power cycle, then OK
* RUN 4: Started from the first time
* RUN 5: Started from the first time
* RUN 6: Bootup OK, no ping (Destination Host Unreachable), retrying GW loading, no change, retrying one more time, then OK
* RUN 7: Started from the first time
* RUN 8: Started from the first time
* RUN 9: Started from the first time
* RUN 10: Started from the first time
* RUN 11: Started from the first time
* RUN 12: Started from the first time
* RUN 13: Started from the first time
* RUN 14: Started from the first time
* RUN 15: Started from the first time

Conclusion:

Boot failure is a *rare* event. However, it's confirmed to exist.

## Issue 2

Issue: It seems that there is no clock on FMC1 CLK0. This clock is observed to identify if clocking circut on FMC works fine.

Steps:

1. Verify that this setup can work.
