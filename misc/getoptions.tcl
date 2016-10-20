
set exps {
    {^ {8}\[(-\w+) (\w+)\]\s+\((.*)$}
    {^ {8}(-\w+) (\w+)\s+\((.*)$}
    {^ {8}\[(\w+)()\]\s+\((.*)$}
    {^ {8}(\w+)()\s+\((.*)$}
    {^ {8}\[(-\w+)()\]\s+\((.*)$}
    {^ {8}(-\w+)()\s+\((.*)$}
    {^ {8}\[(-\w+) (\w+)\]()$}
    {^ {8}(-\w+) (\w+)()$}
    {^ {8}\[(\w+)()\]()$}
    {^ {8}(\w+)()()$}
    {^ {8}\[(-\w+)()\]()$}
    {^ {8}(-\w+)()()$}
}

proc export_option {option val coltype} {
    if {$val != ""} {
        puts $::dst "    $option $coltype"
    } elseif {[string index $option 0] == "-"} {
        puts $::dst "    $option _noval"
    } else {
        puts $::dst "    nkwarg_$::nkwargidx $coltype"
        incr ::nkwargidx
    }
}

proc parsecomment {comment} {
    foreach coltype {lib_cell cell pin port net clock} {
        if {[string first $coltype $comment] >= 0} {
            return $coltype
        }
    }
    return str
}

proc getcoltype {comment option} {
    switch -- $option {
        -waveform -
        -period -
        -name -
        -analysis_type -
        -min -
        -max -
        condition -
        -corners -
        -edges -
        -duty_cycle -
        -group_path -
        -dynamic -
        -priority -
        -edge_shift -
        -comment {
            return str
        }
        -master_clock -
        -clock -
        -from -
        -rise_from -
        -fall_from -
        -to -
        -rise_to -
        -fall_to {
            return clock
        }
        -lib_cell {
            return lib_cell
        }
        -reference_pin -
        -from_pin {
            return pin
        }
        uncertainty -
        -setup -
        -hold -
        -weight -
        value -
        delay_value -
        derate_value -
        delay -
        -multiply_by -
        transition -
        path_multiplier -
        -critical_range -
        -input_transition_rise -
        -input_transition_rise -
        -devide_by -
        -multiply_by -
        -value {
            return num
        }
        -through -
        -rise_through -
        -object_list -
        -fall_through {
            return cell
        }
        -library -
        -min_library -
        -max_library {
            return lib
        }
        default {
            return [parsecomment $comment]
        }
    }
}


# ---- main ----

set tool "icc2"
set repo [file dirname [file dirname [info script]]]
set cmdlist [split [read [open [file join $repo "lib" "cmd.${tool}.list"] "r"]] "\n"]
set dst [open [file join $repo "lib" "cmdopts.${tool}.cfg"] "w"]

foreach cmd $cmdlist {
    if {$cmd eq ""} {continue}
    puts -nonewline stdout "Processing command $cmd ..."
    # use global variable to implement static variable in proc "export_option"
    set nkwargidx 0
    if {[catch {redirect -variable help {$cmd -help}} msg]} {
        puts stdout " FAILED"
        continue
    }
    set help [split $help "\n"]
    foreach line $help {
        puts $dst "# $line"
    }
    puts $dst "set opts%$cmd \{"
    foreach line $help {
        foreach exp $exps {
            if {[regexp -- $exp $line match option val comment] > 0} {
                set coltype [getcoltype $comment $option]
                export_option $option $val $coltype
                break
            }
        }
    }
    puts $dst "\}\n"
    puts stdout ""
}

close $dst
