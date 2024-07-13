function rgb = colormap_value(index, total, map)

nind = round(index / total);
rgb = map(nind, :);

end