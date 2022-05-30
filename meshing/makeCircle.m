function [gd] = makeCircle(origin, radius, scale)
%makeCircle Take origin and radius and make a circle.
%   origin - Origin is a point (x, y).
%
%   radius - Radius of the circle.
%
%   scale - The scale factor.

gd = [
    1;
    origin(1) * scale;
    origin(2) * scale;
    radius * scale
];

end

