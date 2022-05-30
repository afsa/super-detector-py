function [gd] = makePolygon(points, scale)
%makePolygon Take vertex points and make a polygon.
%   points - The input points needs to be an n x 2 matrix and the points 
%   need to be in counter clockwise order.
%   
%   scale - The scale factor.

gd = [
    3;
    size(points, 1);
    points(:, 1) * scale;
    points(:, 2) * scale
    ];

end

