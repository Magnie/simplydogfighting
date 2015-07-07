# Copyright (c) 2011, Chandler Armstrong (omni dot armstrong at gmail dot com)
# see LICENSE.txt for details




"""
line segment object
"""




from math import sqrt

from pygame import Rect




class Line(object):
    """line segment object"""


    def __init__(self, *a):
        """
        construct a line segment object
        arguments must be one of the following:
        two two-place tuples of two numbers each: ((p_x, p_y), (q_x, q_y))
        four numbers: (p_x, p_y, q_x, q_y)
        a Line object
        """
        if len(a) == 1: a = a[0] # a is a Line object
        elif len(a) == 4: a = [(a[0], a[1]), (a[2], a[3])] # (p_x, p_y, q_x, q_y)

        assert len(a) == 2
        for s in a: assert len(s) == 2
        self.p, self.q = a


    def __len__(self): return 2


    def __getitem__(self, i):        
        return (self.p, self.q)[i]

    
    def __iter__(self):        
        return iter(self.p, self.q)


    def __repr__(self):
        return str(self.p) + ', ' + str(self.q)


    @property
    def rect(self):
        """return the AABB, as a pygame rect, of self"""
        p, q = self.p, self.q
        x, y = [min(e) for e in zip(p, q)]
        w = abs(p[0] - q[0])
        h = abs(p[1] - q[1])
        return Rect(x, y, w, h)


    @property
    def m(self):
        """return the slope of self"""
        p_x, p_y = self.p
        q_x, q_y = self.q
        if p_x != q_x:
            return (q_y - p_y) / (q_x - p_x)
        else:
            return None


    @property
    def b(self):
        """return the y-intercept of self"""
        p_x, p_y = self.p
        m = self.m
        if m != None: return p_y - (m * p_x)
        else: return None


    @property
    def dist(self):
        """return the distance covered, or length, of self"""
        p_x, p_y = self.p
        q_x, q_y = self.q
        return sqrt((q_x - p_x)**2 + (q_y - p_y)**2)


    @property
    def delta(self):
        """
        return a vector representing the difference between the endpoints of
        self
        """
        p_x, p_y = self.p
        q_x, q_y = self.q
        return (q_x - p_x, q_y - p_y)


    def intersection(self, *a):
        """
        return the point of intersection between self and other
        a must be an argument list that can be used to construct a Line object
        """
        other = Line(*a)
        self_rect, other_rect = self.rect, other.rect
        # test if AABBs intersect
        if not self_rect.colliderect(other_rect): return None
        self_px, other_px = self.p[0], other.p[0]
        self_m, other_m = self.m, other.m
        self_b, other_b = self.b, other.b
        # test that lines are not parallel
        if self_m != other_m:
            if self_m and other_m: # neither line is verticle
                x = (other_b - self_b) / (self_m - other_m)
                y = (self_m * x) + self_b
            elif self_m == None:   # self is verticle, use other
                x = self_px
                y = (other_m * self_px) + other_b
            elif other_m == None:  # other is verticle, use self
                x = other_px
                y = (self_m * other_px) + self_b
            return (x, y)
        elif self_b == other_b: return self # lines are equal
        else: return None # lines are parallel


    def line_clip(self, rect):
        """
        clip self to rect using liang-barsky
        returns a new line object of self clipped to rect
        """
        p_x, p_y = self.p
        delta_x, delta_y = self.delta
        t0, t1 = 0, 1 # initialize min, max scalar

        if delta_x != 0:
            rl = (rect.left - p_x) / delta_x    # clipping scalar to left edge
            rr = (rect.right - p_x) / delta_x   # clipping scalar to right edge
            if delta_x > 0:                     # if p is leftmost point
                if (rl > t0) and (0 <= rl <= 1): t0 = rl
                if (rr < t1) and (0 <= rr <= 1): t1 = rr
            else:                               # else p is rightmost point
                if (rl < t1) and (0 <= rl <= 1): t1 = rl
                if (rr > t0) and (0 <= rr <= 1): t0 = rr

        if delta_y != 0:
            rb = (rect.bottom - p_y) / delta_y  # clipping scalar to bottom edge
            rt = (rect.top - p_y) / delta_y     # clipping scalar to top edge
            if delta_y > 0:                     # if p is topmost point
                if (rb < t1) and (0 <= rb <= 1): t1 = rb
                if (rt > t0) and (0 <= rt <= 1): t0 = rt
            else:                               # else p is bottommost point
                if (rb > t0) and (0 <= rb <= 1): t0 = rb
                if (rt < t1) and (0 <= rt <= 1): t1 = rt

        if t0 > t1: return False

        return Line(p_x + (t1 * delta_x),
                    p_y + (t1 * delta_y),
                    p_x + (t0 * delta_x),
                    p_y + (t0 * delta_y))


    def line_trace(self):
        """return integer coordinates, or pixels, crossed by self"""
        s = set() # coordinates crossed by self
        delta_x, delta_y = self.delta
        p_x, p_y = self.p
        q_x, q_y = self.q
        m, b = self.m, self.b
        s.add((p_x, p_y))

        if (m) or (abs(m) >= 1): # rise > run
            m = 1 / m    # rotate m by 90 degrees
            b = -(b * m) # rotate b by 90 degrees
            # determine direction of p_y to q_y
            if delta_y < 0: delta_y = -1
            else: delta_y = 1
            # trace from p_y to q_y
            while p_y != q_y:
                p_y += delta_y
                s.add((round((m * p_y) + b), p_y))

        else: # else rise < run
            # determine direction of p_x to q_x
            if delta_x < 0: delta_x = -1
            else: delta_x = 1
            # trace from p_x to q_x
            while p_x != q_x:
                p_x += delta_x
                s.add((p_x, round((m * p_x) + b)))

        return s
