function lv_seq_quickdump(date, num)

lv_seq_dump(lv_seq_read(struct('num', num,'date',date)),...
    sprintf('C:\\Users\\chinl\\Documents\\SeqDumps\\Seq%04d%02d%02d_%d.txt', ...
    date(1), date(2), date(3), num));