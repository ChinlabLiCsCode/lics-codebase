function smart_fig_export(fig, name)


% export_fig([name '.pdf'], fig, "-transparent");
exportgraphics(fig, [name '.pdf'], 'BackgroundColor','none','ContentType','vector')
savefig(fig, [name '.fig']);

