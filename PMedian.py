import sys
from gamspy import Container, Set, Parameter, Variable, Equation, Model, Sum, Sense

m = Container()

# Sets
i = Set(m, name="i", description="customers")
j = Set(m, name="j", description="potential sites")

# Parameters
d = Parameter(m, name="d", domain=[i, j], description="distance between i and j")
w = Parameter(m, name="w", domain=i, description="weight/demand of customer i")
p_num = Parameter(m, name="p_num", description="number of facilities to locate")

# Variables
x = Variable(m, name="assign", domain=[i, j], type="binary", description="assignment of i to j")
y = Variable(m, name="locate", domain=j, type="binary", description="site selection")

# Equations
one_site = Equation(m, name="one_site", domain=i, description="each customer assigned once")
one_site[i] = Sum(j, x[i, j]) == 1

bound = Equation(m, name="bound", domain=[i, j], description="assignment bound by location")
bound[i, j] = x[i, j] <= y[j]

count = Equation(m, name="count", description="limit total facilities to p")
count[...] = Sum(j, y[j]) == p_num

# Objective
obj = Sum((i, j), w[i] * d[i, j] * x[i, j])

p_median = Model(
    container=m,
    name="p_median",
    equations=[one_site, bound, count],
    problem="MIP",
    sense=Sense.MIN,
    objective=obj
)

# Data
i.setRecords(["C1", "C2", "C3", "C4"])
j.setRecords(["S1", "S2", "S3"])
w.setRecords([("C1", 10), ("C2", 20), ("C3", 30), ("C4", 40)])
p_num.setRecords(2)
d.setRecords([
    ("C1", "S1", 2), ("C1", "S2", 10), ("C1", "S3", 8),
    ("C2", "S1", 9), ("C2", "S2", 3),  ("C2", "S3", 5),
    ("C3", "S1", 4), ("C3", "S2", 6),  ("C3", "S3", 2),
    ("C4", "S1", 10), ("C4", "S2", 2), ("C4", "S3", 7)
])

p_median.solve(output=sys.stdout)
