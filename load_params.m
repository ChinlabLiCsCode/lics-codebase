function load_params(today, replacedate)
% LOAD_PARAMS Load the parameters for the current day
%
%   LOAD_PARAMS loads the parameters for the current day. If no day is
%   specified, the current day is used. 
%   
%   LOAD_PARAMS(TODAY) loads the parameters for the day specified by TODAY.
%   TODAY should be a vector of the form [YYYY, MM, DD].
%
%   LOAD_PARAMS(TODAY, REPLACEDATE) loads the params corresponding to 
%   TODAY but then replaces the date field. If REPLACEDATE is just 'true',
%   it uses TODAY. Otherwise you can specify a specific date.
%
%   The parameters are loaded from the
%   folder specified as 'loadparams' in your localpath.m file. The
%   parameters are loaded into the workspace. This function will search 
%   for the most recent parameters file that is not in the future, so you 
%   don't have to have a parameters file for every single day, just for 
%   when you actually change the parameters. 
%


% Use today's date if no day is supplied
if nargin < 1
    clk = clock;
    today = [clk(1), clk(2), clk(3)];
end

% Don't overwrite the date if it isn't specified
if nargin < 2
    replace = false;
elseif isnumeric(replacedate)
    replace = true;
elseif replacedate
    replace = true;
    replacedate = today;
else
    replace = false;
end

% List all files in the folder
folderpath = localpath('loadparams');
files = dir(fullfile(folderpath, 'params_*.mat')); 

% Get today's date
today = str2double(sprintf('%04.4d%02.2d%02.2d', today(1), today(2), today(3)));

% Loop through each file and extract its date
fdays = zeros(length(files), 1);
for i = 1:length(files)
    fname = files(i).name;
    
    % Extract the date part of the file name 
    C = regexpi(fname, '\d{8}', 'match', 'once');
    fdays(i) = str2double(strrep(C,',','.')); 
end

% Sort the files by date 
[fdays, idx] = sort(fdays);
files = files(idx);

% Remove future days 
future = fdays > today;
files = files(~future);

% The right day to load is the last non-future day 
load_file = files(end);

% Load the params
params = load(fullfile(folderpath, load_file.name), 'params*');

% Transport the params into the workspace
names = fieldnames(params);
for i = 1:length(names)
    if replace
        params.(names{i}).date = replacedate;
    end
    assignin('base', names{i}, params.(names{i}));
end

end

