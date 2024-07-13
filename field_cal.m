function Bs = field_cal(in_seps,freq,shots,tf,h_flag)

make_constants

if nargin<5 || isempty(h_flag)
    h_flag = true;
end

if h_flag
    in_seps = sqrt(2)*in_seps;
end

find_B = @(f) fzero(@(B) breit_rabi(B,4,1,133)-breit_rabi(B,3,-1,133)-f,900);

%Calibrations: Energy shift (in MHz)/G change in field
cal33 = -((breit_rabi(find_B(freq(1))+.5,3,-1,133))-(breit_rabi(find_B(freq(1))-.5,3,-1,133)));
% cal44 = ((breit_rabi(find_B(freq)+.5,4,1,133))-(breit_rabi(find_B(freq)-.5,4,1,133)));
% cal = cal33+cal44;

if length(freq)>1 && nargin>2 && ~isempty(shots)
    freqs = freq(1)*ones(size(in_seps));
    a = 1;
    for xi = 1:length(freqs)
        if length(shots)>a && xi==shots(a+1)
            a = a+1;
        end
        freqs(xi) = freq(a);
    end
    freq = freqs;
elseif size(freq,1)>1 && size(freq,1) == size(in_seps,1) && size(freq,2) == 1 && size(in_seps,2)>1
    freqs = 0*in_seps;
    for xi = 1:size(in_seps,2)
        freqs(:,xi) = freq; 
    end
    freq = freqs;
elseif size(freq,2)>1 && size(freq,2) == size(in_seps,2) && size(freq,1) == 1 && size(in_seps,1)>1
    freqs = 0*in_seps;
    for xi = 1:size(in_seps,1)
        freqs(xi,:) = freq; 
    end
    freq = freqs;
end


%Get approximate field
Bs = 0*freq;


for a = 1:size(freq,1)
    for b = 1:size(freq,2)
        Bs(a,b) = find_B(freq(a,b));
    end
end

%Trapping frequency
if nargin<4 || isempty(tf)
    tf = 6.4801*sqrt(Bs/898.2);
end

om = (tf*(2*pi));
k = om.^2*133*amu;
E_shifts = k/2.*(in_seps/2).^2;
B_shifts = E_shifts/cal33/1e6/h;
Bs = Bs+B_shifts;