function smart_fig_export(fig, name)


% export_fig([name '.pdf'], fig, "-transparent");
exportgraphics(fig, strcat(name, '.pdf'), 'BackgroundColor','none','ContentType','vector')
savefig(fig, strcat(name, '.fig'));
saveas(fig, strcat(name, '.png'));