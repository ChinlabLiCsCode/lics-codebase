plot_defaults;

N = 13;
colormatrix = zeros(1, N, 3);
colormatrix(:) = co(:);
figure();
imshow(colormatrix, "InitialMagnification", "fit");
axis image;
axis on;
box off;
yticks([]);
xticks(1:N);
xticklabels({"blue", "orange", "yellow", "purple", "green", "lightblue", "maroon", ...
    "red", "lavender", "gray", "teal", "brown", "magenta"});


