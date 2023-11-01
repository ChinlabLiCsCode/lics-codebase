function smart_fig_export(fig, name)


export_fig([name '.pdf'], fig);
savefig(fig, [name '.fig']);

