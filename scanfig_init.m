function h = scanfig_init(params, figname)


% Initialize the plot
h = struct();
h.fig = figure('Name', figname, 'NumberTitle', 'off', 'Units', 'normalized', 'OuterPosition', [0 0 1 1]);

% Get plots from params 
plts = params.pltinfo;

nrow = length(plts);
for r = 1:nrow
    % first entry in each row is the number of cols for subplot
    ncol = plts{r}{1};
    for c = 2:length(plts{r})
        p = plts{r}{c};
        
        ax = subplot(nrow, ncol, ncol*(r-1)+p{2});
        h.(p{1}) = ax;
        
    end
end
end