function save_params(today)

% Use today's date if no day is supplied
if nargin < 1
    clk = clock;
    today = [clk(1), clk(2), clk(3)];
end

% Get path from localpath.m
folderpath = localpath('saveparams');

% Make name 
name = sprintf('params_%04.4d%02.2d%02.2d.mat', today(1), today(2), today(3));

% Make full path
savepath = fullfile(folderpath, name);

% Make full command
cmd = ['save(''', savepath, ''', ''params*'')'];
disp(cmd);

% Evaluate the save command in the base workspace
evalin('base', cmd);

end