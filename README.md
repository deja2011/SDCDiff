# SDCDiff

Comparing two SDC (Synopsys Design Constraint) files

----
## SYNTAX & ARGS

NAME:
```
aid_diff_sdc    diff two sdc files
```
SYNTAX:

```
command aid_diff_sdc
[-product product]
[-compile_log compilelog]
file1
file2
```

Data Types
```
product         string
compilelog      string
file1           string
file2           string
```

ARGUMENTS
```
-product        product
    Synopsys product name. Only "dcrt" and "icc2" are supported. If this option is omitted, 
    its value will be inferred from $synopsys_program_name. If $synopsys_program_name is also 
    missing, option value defaults to "dcrt".

-compile_log    compilelog
    Path to the compile log file. This option is designed for the "constraint preservation"
    project in Descartes only. Please skip this option if you don't need it. If this option is
    specified, the compile log would be considered during verification, and verify result may 
    be different from when this option is omitted.

file1
    SDC file 1

file2
    SDC file 2
```
----
## USAGE

This command is used to differentiate two SDC files.

SDC files are exported by the `write_sdc` command in DC/Descartes/ICC/ICC2 or other Synopsys products. A typical SDC file is a list of flattened SDC commands. It would only contain SDC commands like `create_clock` or `set_input_delay`, and netlist query commands like `get_cells` or `get_pins`. No logic control commands such as `if`, `foreach`, `switch` are expected in an SDC file. 

Many SDC commands involves a collection of design objects so it can be structured as one command that constraints a large collection, or can be sturctured as several commands and each of them constraints a small collection. For example, following two SDC files are literally different but indeed have the same effect.

File 1:
```
group_path -name group_1 -from [get_cells {A B}] -to [get_cells {C D}]
```
File 2:
```
group_path -name group_1 -from [get_cells A] -to [get_cells C]
group_path -name group_1 -from [get_cells A] -to [get_cells D]
group_path -name group_1 -from [get_cells B] -to [get_cells C]
group_path -name group_1 -from [get_cells B] -to [get_cells D]
```
_sdcdiff_ will first decompose all SDC commands in both input SDC files into atomic SDC commands, then sort the atomic commands, and finally differentiate two SDC files. An **atomic** SDC command is an SDC command in which all arguments that are collections have the length of one. All `group_path` commands as presented in File 2 in above example are atomic SDC commands.

To parse a normal SDC command and decompose it into atomic SDC commands, some information of option configuration for each SDC command is recorded along this AID command. The supported command list differs among products, and can be reviewed at `lib/cmd.${p}.list`, where `$p` can be either icc2 or dcrt.

----
## Archive

```
|-- README
|-- aid_diff_sdc
|   `-- aid_diff_sdc.tcl
|-- bin
|   |-- comparator.py
|   |-- extractor.py
|   |-- getcmds
|   |-- sdcdiff
|   `-- sdcflat
|-- lib
|   |-- cmd.dc.list
|   |-- cmd.dcrt.list
|   |-- cmd.icc2.list
|   |-- cmdopts.dc.cfg
|   |-- cmdopts.dcrt.cfg
|   `-- cmdopts.icc2.cfg
`-- misc
|-- diff_st_and_mt.py
`-- getoptions.tcl
```
- `bin/comparator.py`
    * A Python Process module to compare command pools for file 1 and file 2, and remove common commands if there are any.
- `bin/extractor.py`
    * A Python Process module to extract flattened commands from SDC file into a command pool which is shared with comparator.
- `bin/getcmds`
    * A tclparser script to get command statistics from SDC file. Very slow. Will be replaced by Python codes in coming version.
- `bin/sdcdiff`
    * Program entrance.
- `bin/sdcflat`
    * A tclparser script to flatten tcl commands in SDC file and output flattened commands in stream.
- `bin/aid_diff_sdc.tcl`
    * A PV AID command implementation. A wrapper of sdcdiff.
- `lib/cmd.*.list`
    * A text file of command list in synopsys products.
- `lib/cmdopts.*.cfg`
    * A database in tcl syntax that definies all command configurations.
- `misc/diff_st_and_mt.py`
    * Compare runtime performance of single core and multi core solutions.
- `misc/getoptions.tcl`
    * Parse command configuration from command help page.
