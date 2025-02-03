function smart_fig_export(fig, name, varargin)

p = inputParser;
addParameter(p, 'appendpdf', false, @(x) islogical(x)); % append to a pdf instead of
addParameter(p, 'justpdf', true, @(x) islogical(x)); % do just pdf
addParameter(p, 'resolution', 150, @(x) isnumeric(x)); % save resolution
parse(p, varargin{:});
appendpdf = p.Results.appendpdf;
justpdf = p.Results.justpdf;
resolution = p.Results.resolution;

if ~justpdf
    exportgraphics(fig, strcat(name, '.pdf'), 'BackgroundColor','none', ...
        'ContentType','vector', 'Append', appendpdf)
    exportgraphics(fig,strcat(name, '.png'),'Resolution',300)
    savefig(fig, strcat(name, '.fig'));
else
    exportgraphics(fig, strcat(name, '.pdf'), 'BackgroundColor','none', ...
        'ContentType','vector','Append',appendpdf)
end