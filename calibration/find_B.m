%invert Breit-Rabi to go from microwave freq to field
function out=find_B(f)
sz = length(f);
out = zeros([1 sz]);
for i=1:sz
    outtmp=fzero(@(B) breit_rabi(B,4,1,133) - breit_rabi(B,3,-1,133)-f(i),900);
    out(i) = outtmp;
end
end

