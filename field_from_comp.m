function [out_field in_comp_round] = field_from_comp(in_comp,in_ah,in_shim,varargin)

% round the computer field first

in_comp_big = round((in_comp+10)/20*65536);
in_comp_round = 20*in_comp_big/65536-10;

if nargin<4 || isempty(varargin)
%     varargin = {'traditional'};
    varargin = {892.6};
end

[A, B] = get_field_params(varargin{:});

if nargin<2 || isempty(in_ah)
    in_ah_round = 0;
else
    in_ah_big = round((in_ah+10)/20*65536);
    in_ah_round = 20*in_ah_big/65536-10;
end
if nargin<3 || isempty(in_shim)
    in_shim_round = 0;
else
    in_shim_big = round((in_shim+10)/20*65536);
    in_shim_round = 20*in_shim_big/65536-10;
end

out_field = A*[in_comp_round;in_ah_round;in_shim_round]+B;