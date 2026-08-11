function rgb = cmap_val(index, total, map)

nind = round(256 * index / total);
rgb = map(nind, :);

end