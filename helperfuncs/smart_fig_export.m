function smart_fig_export(fig, name, varargin)

p = inputParser;
addParameter(p, 'appendpdf', false, @(x) islogical(x)); % append to a pdf instead of
parse(p, varargin{:});
appendpdf = p.Results.appendpdf;

if ~appendpdf
    exportgraphics(fig, strcat(name, '.pdf'), 'BackgroundColor','none', ...
        'ContentType','vector')
    savefig(fig, strcat(name, '.fig'));
    saveas(fig, strcat(name, '.png'));
else
    exportgraphics(fig, strcat(name, '.pdf'), 'BackgroundColor','none', ...
        'ContentType','vector','Append',true)
end