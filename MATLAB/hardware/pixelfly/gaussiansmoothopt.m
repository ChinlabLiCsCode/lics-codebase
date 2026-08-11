function result = gaussiansmoothopt(mtx, pixels, sigma, varargin)
%GAUSSIANSMOOTH(mtx, pixels, sigma) gaussian averages neighboring pixels of a matix, out to #pixels away per point.
%Arguments
% mtx - The matrix
% pixels - How many pixels away from the current point to consider.
% Uses a box of dimension (2*pixels+1)
% sigma - The sigma of the gaussian function.
%
%Note: Large values of 'pixels' may result in edge effects.

h=fspecial('gaussian', 2*pixels+1, sigma);

result=imfilter(mtx, h, varargin{:});