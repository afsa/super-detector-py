function [g] = makeGeometry(sf, ns, varargin)
%makeGeometry Generate a geometry representation from geometric shapes.
%   sf is the formula that specifies how the shapes are to be joined (e.g.
%   'R1 + R2')
%   ns is the names of the shapes (e.g. char('R1', 'R2'))
%   The matrices containing the shapes should be given as parameters (e.g.
%   makeGeometry('R1 + R2', char('R1', 'R2'), R1, R2)).

% Compute the padding needed
max_length = 0;
for i = 1:length(varargin)
    max_length = max(length(varargin{i}), max_length);
end

% Pad the geometric shapes to the geometry matrix
gm = zeros(max_length, length(varargin));
for i = 1:length(varargin)
    gm(:, i) = [varargin{i}; zeros(max_length - length(varargin{i}),1)];
end

% Generate a geometry from the geometry matrix and the formula.
[g, bt] = decsg(gm,sf,ns');

% Remove face boundaries
g = csgdel(g, bt);

end

