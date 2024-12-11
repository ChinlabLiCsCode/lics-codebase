function smart_fig_export(fig, name, varargin)

p = inputParser;
addParameter(p, 'appendpdf', false, @(x) islogical(x)); % append to a pdf instead of
addParameter(p, 'justpdf', true, @(x) islogical(x)); % do just pdf
parse(p, varargin{:});
appendpdf = p.Results.appendpdf;
justpdf = p.Results.justpdf;

if ~justpdf
    exportgraphics(fig, strcat(name, '.pdf'), 'BackgroundColor','none', ...
        'ContentType','vector', 'Append', appendpdf)
    savefig(fig, strcat(name, '.fig'));
    saveas(fig, strcat(name, '.png'));
else
    exportgraphics(fig, strcat(name, '.pdf'), 'BackgroundColor','none', ...
        'ContentType','vector','Append',appendpdf)
end