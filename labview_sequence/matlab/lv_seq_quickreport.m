function lv_seq_quickreport(date, num, ch)

lv_seq_channel_report(lv_seq_read(struct('date',date,'num',num)), ch, 1);