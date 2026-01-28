import sys
from gamspy import Container, Set, Parameter, Variable, Equation, Model, Sum, Sense

m = Container()

# Sets
i = Set(m, name="i", description="customers")
j = Set(m, name="j", description="potential facilities")

# Parameters
capacity = Parameter(m, name="cap", domain=j, description="capacity of facility j")
demand = Parameter(m, name="dem", domain=i, description="demand of customer i")
f = Parameter(m, name="f", domain=j, description="fixed cost to open facility j")
c = Parameter(m, name="c", domain=[i, j], description="shipping cost from j to i")

# Variables
x = Variable(m, name="x", domain=[i, j], type="positive", description="shipment quantity")
y = Variable(m, name="y", domain=j, type="binary", description="facility status")

# Equations
demand_cons = Equation(m, name="demand_cons", domain=i)
demand_cons[i] = Sum(j, x[i, j]) >= demand[i]

capacity_cons = Equation(m, name="capacity_cons", domain=j)
capacity_cons[j] = Sum(i, x[i, j]) <= capacity[j] * y[j]

# Objective
obj = Sum(j, f[j] * y[j]) + Sum((i, j), c[i, j] * x[i, j])

facility_loc = Model(
    container=m,
    name="facility_loc",
    equations=[demand_cons, capacity_cons],
    problem="MIP",
    sense=Sense.MIN,
    objective=obj
)

# Data
i.setRecords(["C1", "C2", "C3"])
j.setRecords(["F1", "F2"])
demand.setRecords([("C1", 80), ("C2", 270), ("C3", 250)])
capacity.setRecords([("F1", 500), ("F2", 500)])
f.setRecords([("F1", 1000), ("F2", 1000)])
c.setRecords([
    ("C1", "F1", 4), ("C1", "F2", 5),
    ("C2", "F1", 6), ("C2", "F2", 4),
    ("C3", "F1", 3), ("C3", "F2", 5)
])

facility_loc.solve(output=sys.stdout)
