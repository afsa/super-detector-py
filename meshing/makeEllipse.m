function [gd] = makeEllipse(origin, xRadius, yRadius, scale)
%makeEllipse Take origin, x radius and y radius to generate an ellipse.
%   origin - Origin is a point (x, y).
%
%   xRadius - The radius of the x axis.
%
%   yRadius - The radius of the y axis.
%
%   scale - The scale factor.


gd = [
    4;
    origin(1) * scale;
    origin(2) * scale;
    xRadius * scale;
    yRadius * scale
];

end

