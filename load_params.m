function params = load_params(load_day)

    if nargin < 1
        clk = clock;
        load_day = [clk(1), clk(2), clk(3)];
    end

    % List all files in the folder
    folderpath = localpath('params');
    files = dir(fullfile(folderPath, 'params_*.mat')); % Adjust the file extension as needed

    % Get today's date
    load_day = str2double(sprintf('%d%d%d', load_day(1), load_day(2), load_day(3)));

    % Initialize variables to store the most recent date and file path
    recent_day = 0;
    recent_file = '';

    % Loop through each file and extract its date
    for i = 1:length(files)
        fname = files(i).name;
        
        % Extract the date part of the file name 
        fday = regexpi(fname, '\d{8}', 'match', 'once');
        
        % Compare and update 
        if ~isempty(fday) && (fday > recent_day) && (fday <= load_day)
            recent_day = fday;
            recent_file = fname;
        end
    end
    
    % load the params
    params = load(fullfile(folderpath, recent_file), 'params*');

end


