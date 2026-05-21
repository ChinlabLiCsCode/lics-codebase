function out_struct = lv_seq_get_channel_by_no(in_seq, in_channel_no)

out_struct.chan_no = in_channel_no;

if in_seq.version < 4
    if in_channel_no < 16
        % primary analog group
        out_struct.ival = in_seq.primary_analog.ival(in_channel_no+1);
        out_struct.name = in_seq.primary_analog.name{in_channel_no+1};
        out_struct.is_analog = in_seq.primary_analog.is_analog(in_channel_no+1);
    elseif in_channel_no < 46
        % digital group
        out_struct.ival = in_seq.digital.ival(in_channel_no-15);
        out_struct.name = in_seq.digital.name{in_channel_no-15};
        out_struct.is_analog = in_seq.digital.is_analog(in_channel_no-15);
    else
        % secondary analog group
        out_struct.ival = in_seq.secondary_analog.ival(in_channel_no-45);
        out_struct.name = in_seq.secondary_analog.name{in_channel_no-45};
        out_struct.is_analog = in_seq.secondary_analog.is_analog(in_channel_no-45);
    end
else
    if in_channel_no < 24
        % primary analog group
        out_struct.ival = in_seq.primary_analog.ival(in_channel_no+1);
        out_struct.name = in_seq.primary_analog.name{in_channel_no+1};
        out_struct.is_analog = in_seq.primary_analog.is_analog(in_channel_no+1);
    elseif in_channel_no < 86
        % digital group
        out_struct.ival = in_seq.digital.ival(in_channel_no-23);
        out_struct.name = in_seq.digital.name{in_channel_no-23};
        out_struct.is_analog = in_seq.digital.is_analog(in_channel_no-23);
    else
        % secondary analog group
        out_struct.ival = in_seq.secondary_analog.ival(in_channel_no-85);
        out_struct.name = in_seq.secondary_analog.name{in_channel_no-85};
        out_struct.is_analog = in_seq.secondary_analog.is_analog(in_channel_no-85);
    end
end