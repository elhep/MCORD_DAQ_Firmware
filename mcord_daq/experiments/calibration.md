
afedrv.SetDac(0, 55, 55)
afedrv.SetDac(1, 55, 55)



afedrv.SetDigRes(0, 0, 200)
afedrv.SetDigRes(0, 1, 200)
afedrv.SetDigRes(1, 0, 200)
afedrv.SetDigRes(1, 1, 200)

misc.HVon(0)
misc.HVon(1)

pyb.Pin.cpu.E8.init(pyb.Pin.OUT_PP, pyb.Pin.PULL_NONE)
pyb.Pin.cpu.E8.value(1)

afedrv.SetCal(0, 0)
afedrv.SetCal(0, 1)
afedrv.SetCal(1, 0)
afedrv.SetCal(1, 1)

Make a series of 100 us pulses with 1s separation

for _ in range(100)

