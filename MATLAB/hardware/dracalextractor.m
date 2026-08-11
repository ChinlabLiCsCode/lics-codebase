function [times, alldat] = dracalextractor(fname)

opts = detectImportOptions(fname);
opts.VariableNamesLine = 7;
opts.DataLines = [10 Inf];
alldat = readtable(fname, opts);

times = table2array(alldat(:, 1));

end