function lv_seq_quickdump(date, num)

lpath = localpath('lvseqdump');
lv_seq_dump(lv_seq_read(struct('num', num,'date',date)),...
    sprintf(lpath, date(1), date(2), date(3), num));