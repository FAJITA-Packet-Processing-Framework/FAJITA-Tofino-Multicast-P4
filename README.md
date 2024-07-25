# FAJITA Tofino Multicaster

This P4 program takes incoming packets, manipulates their source IP address and multicasts them towards the NF, in order to increase the offered load.

You need a Tofino to build and run the `fajita_mcast` program. The default configuration uses four multicast ports.

To build the code, use the following command:

```
/path/to/p4_build.sh /path/to/fajita_mcast.p4
```

`fajita_mcast.p4` has been tested on SDE 9.8.0.

## Configuration

### Change Script Path

The `setup.py` script assumes that it is executed in `/home/tofino/labs/FAJITA-Tofino-Multicast-P4` folder.
You can change this folder by changing the `script_path` variable in `setup.py` (line 96):

```python3
script_path = os.path.join(os.environ['HOME'], "labs", "FAJITA-Tofino-Multicast-P4")
```

### Change Port Numbers

To change the ports in the `fajita_mcast` program, you need to:
- Change the `fajita_mcast.p4` defines:
```p4
const PortId_t PKTGEN_PORT = 52;

const PortId_t INPUT_PORT_1 = 188;
const PortId_t INPUT_PORT_2 = 180;
const PortId_t INPUT_PORT_3 = 172;
const PortId_t INPUT_PORT_4 = 164;
```

- Change the `setup*.py` files:
```python3
MCAST_PORTS = [188, 180, 172, 164]
```

- Change the `run_pd_rpc/setup.py` file:
```python3
PKTGEN_PORT = 52
MCAST_PORTS = [188, 180, 172, 164]
```

You then need to recompile the P4 program.

### Change the Number of Multicast Copies

By default `fajita_mcast` will create four copies of each incoming packet.
To change the number of copies, change the variable `N_MULTICAST` in `run_pd_rpc/setup.py`. If `0` is specified, it will fallback to one copy.

### Enable/Disable Recirculation

By default, `fajita_mcast` has the `ENABLE_RECIRCULATION` set to `1` in `setup.py`.
This value will create 2x`N_MULTICAST` copies of each packet, since one of the packet copies is sent to the recirculation port (by default `196` that is the recirculation port of pipe 1).
The additional copy will be then multicasted again on the `INPUT_PORT_*` enabled for recirculation.

You can disable this behaviour by setting `ENABLE_RECIRCULATION` to `0`.